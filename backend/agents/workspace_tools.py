"""Project workspace tools used by coding agents.

These tools operate on the database-backed project files. A later runtime layer
can swap this service to a real filesystem while keeping the API contract.
"""
import difflib
from typing import Dict, List, Optional

from django.db import transaction
from django.utils import timezone

from files.models import File, FileVersion
from tasks.models import Task, TaskAction


class WorkspaceToolError(ValueError):
    """Raised when an agent workspace operation cannot be completed."""


def infer_language(path: str) -> str:
    extension = path.rsplit('.', 1)[-1].lower() if '.' in path else ''
    return {
        'py': 'python',
        'js': 'javascript',
        'jsx': 'javascript',
        'ts': 'typescript',
        'tsx': 'typescript',
        'json': 'json',
        'md': 'markdown',
        'html': 'html',
        'css': 'css',
    }.get(extension, 'plaintext')


class ProjectWorkspace:
    """High-level, audited operations for a project's files."""

    def __init__(self, project, user):
        self.project = project
        self.user = user

    def read_file(self, path: str) -> Dict:
        file = self._get_file(path)
        task = self._create_task('Read file', f'Read {path}')
        self._record_action(task, 'file_read', path, {'path': path}, {'size': file.size})
        self._complete_task(task, {'path': path, 'size': file.size})
        return self._serialize_file(file)

    def search(self, query: str, limit: int = 20) -> Dict:
        if not query:
            raise WorkspaceToolError('Search query is required.')

        files = File.objects.filter(project=self.project, is_directory=False)
        matches: List[Dict] = []
        query_lower = query.lower()

        for file in files:
            path_matches = query_lower in file.path.lower()
            content_index = file.content.lower().find(query_lower)
            if not path_matches and content_index == -1:
                continue

            line_number = None
            preview = ''
            if content_index >= 0:
                before = file.content[:content_index]
                line_number = before.count('\n') + 1
                line_start = file.content.rfind('\n', 0, content_index) + 1
                line_end = file.content.find('\n', content_index)
                if line_end == -1:
                    line_end = len(file.content)
                preview = file.content[line_start:line_end].strip()

            matches.append({
                'id': file.id,
                'name': file.name,
                'path': file.path,
                'language': file.language or infer_language(file.path),
                'line': line_number,
                'preview': preview,
                'path_match': path_matches,
            })
            if len(matches) >= limit:
                break

        task = self._create_task('Search workspace', f'Search for "{query}"')
        self._record_action(task, 'search', query, {'query': query, 'limit': limit}, {'matches': matches})
        self._complete_task(task, {'match_count': len(matches)})
        return {'query': query, 'matches': matches}

    def propose_edit(self, path: str, proposed_content: str, instructions: str = '') -> Dict:
        file = self._get_file(path)
        diff = self.build_diff(path, file.content, proposed_content)
        task = self._create_task('Propose file edit', instructions or f'Propose edit for {path}')
        self._record_action(
            task,
            'code_generate',
            path,
            {'path': path, 'instructions': instructions},
            {'diff': diff, 'proposed_content': proposed_content},
        )
        self._complete_task(task, {'path': path, 'diff': diff})
        return {
            'path': path,
            'original_content': file.content,
            'proposed_content': proposed_content,
            'diff': diff,
            'task_id': task.id,
        }

    @transaction.atomic
    def apply_edit(
        self,
        path: str,
        proposed_content: str,
        expected_original_content: Optional[str] = None,
        change_description: str = 'Agent edit applied',
    ) -> Dict:
        file = self._get_file(path, for_update=True)
        if expected_original_content is not None and file.content != expected_original_content:
            raise WorkspaceToolError('File changed since the edit was proposed.')

        original_content = file.content
        file.content = proposed_content
        file.size = len(proposed_content.encode('utf-8'))
        file.language = file.language or infer_language(file.path)
        file.save()

        latest_version = file.versions.first()
        version_number = (latest_version.version_number + 1) if latest_version else 1
        FileVersion.objects.create(
            file=file,
            version_number=version_number,
            content=file.content,
            changed_by=self.user,
            change_description=change_description,
        )

        diff = self.build_diff(path, original_content, proposed_content)
        task = self._create_task('Apply file edit', change_description)
        self._record_action(
            task,
            'file_write',
            path,
            {'path': path, 'change_description': change_description},
            {'diff': diff, 'version_number': version_number},
        )
        self._complete_task(task, {'path': path, 'version_number': version_number})
        return {**self._serialize_file(file), 'diff': diff, 'task_id': task.id}

    @staticmethod
    def build_diff(path: str, original_content: str, proposed_content: str) -> str:
        return ''.join(difflib.unified_diff(
            original_content.splitlines(keepends=True),
            proposed_content.splitlines(keepends=True),
            fromfile=f'a/{path}',
            tofile=f'b/{path}',
        ))

    def _get_file(self, path: str, for_update: bool = False) -> File:
        if not path:
            raise WorkspaceToolError('File path is required.')
        queryset = File.objects.select_for_update() if for_update else File.objects
        try:
            return queryset.get(project=self.project, path=path, is_directory=False)
        except File.DoesNotExist as exc:
            raise WorkspaceToolError(f'File not found: {path}') from exc

    def _create_task(self, title: str, description: str) -> Task:
        return Task.objects.create(
            project=self.project,
            title=title,
            description=description,
            status='in_progress',
            assigned_to=self.user,
            started_at=timezone.now(),
        )

    def _record_action(self, task: Task, action_type: str, target: str, input_data: Dict, output_data: Dict):
        TaskAction.objects.create(
            task=task,
            action_type=action_type,
            target=target,
            input_data=input_data,
            output_data=output_data,
            status='success',
        )

    def _complete_task(self, task: Task, result: Dict):
        task.status = 'completed'
        task.result = result
        task.completed_at = timezone.now()
        task.save(update_fields=['status', 'result', 'completed_at', 'updated_at'])

    def _serialize_file(self, file: File) -> Dict:
        return {
            'id': file.id,
            'name': file.name,
            'path': file.path,
            'language': file.language or infer_language(file.path),
            'content': file.content,
            'size': file.size,
            'updated_at': file.updated_at,
        }
