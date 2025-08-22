#!/usr/bin/env python3
"""
Git Analysis Module for Nancy Codebase MCP Server
Provides comprehensive Git repository analysis including authorship, history, and collaboration patterns.
Extracted from Nancy's core ingestion service for standalone MCP operation.
"""

import os
import git
from git import Repo, GitCommandError, InvalidGitRepositoryError
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import logging

logger = logging.getLogger(__name__)


class GitAnalyzer:
    """
    Comprehensive Git repository analyzer for authorship, collaboration, and code ownership patterns.
    Extracted from Nancy's GitAnalysisService for standalone MCP operation.
    """
    
    def __init__(self):
        self.repo = None
        self.repo_path = None
        logger.info("GitAnalyzer initialized")
    
    def initialize_repository(self, repo_path: str) -> bool:
        """
        Initialize Git repository for analysis.
        """
        try:
            self.repo_path = os.path.abspath(repo_path)
            
            # Find the git repository root
            current_path = self.repo_path
            while current_path != os.path.dirname(current_path):  # not root directory
                if os.path.exists(os.path.join(current_path, '.git')):
                    self.repo = git.Repo(current_path)
                    self.repo_path = current_path
                    logger.info(f"Git repository found: {self.repo_path}")
                    return True
                current_path = os.path.dirname(current_path)
            
            # Try initializing directly if no .git found in parents
            if os.path.exists(os.path.join(self.repo_path, '.git')):
                self.repo = git.Repo(self.repo_path)
                logger.info(f"Git repository initialized: {self.repo_path}")
                return True
            
            logger.warning(f"No Git repository found at {repo_path} or its parents")
            return False
            
        except (GitCommandError, InvalidGitRepositoryError) as e:
            logger.error(f"Git repository initialization failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error initializing Git repository: {e}")
            return False
    
    def get_file_authorship(self, file_path: str) -> Dict[str, Any]:
        """
        Get comprehensive authorship information for a file including contributors and commit history.
        """
        if not self.repo:
            return {"error": "No repository initialized"}
        
        try:
            relative_path = os.path.relpath(file_path, self.repo_path)
            
            # Get blame information for the file
            blame_data = []
            contributors = set()
            
            try:
                blame = self.repo.blame('HEAD', relative_path)
                
                for commit, lines in blame:
                    author_name = commit.author.name
                    author_email = commit.author.email
                    commit_date = commit.authored_datetime
                    
                    contributors.add(author_name)
                    blame_data.append({
                        "author_name": author_name,
                        "author_email": author_email,
                        "commit_hash": commit.hexsha,
                        "commit_date": commit_date.isoformat(),
                        "lines": len(lines)
                    })
            except Exception as blame_error:
                logger.warning(f"Blame analysis failed for {relative_path}: {blame_error}")
            
            # Get commit history for the file
            commit_history = []
            try:
                commits = list(self.repo.iter_commits(paths=relative_path, max_count=50))
                
                for commit in commits:
                    commit_history.append({
                        "commit_hash": commit.hexsha,
                        "author_name": commit.author.name,
                        "author_email": commit.author.email,
                        "commit_date": commit.authored_datetime.isoformat(),
                        "message": commit.message.strip(),
                        "files_changed": commit.stats.total['files'],
                        "insertions": commit.stats.total['insertions'],
                        "deletions": commit.stats.total['deletions']
                    })
            except Exception as history_error:
                logger.warning(f"Commit history failed for {relative_path}: {history_error}")
            
            # Get file statistics
            try:
                file_stat = os.stat(file_path)
                last_modified = datetime.fromtimestamp(file_stat.st_mtime)
                file_size = file_stat.st_size
            except Exception as stat_error:
                logger.warning(f"File stat failed for {file_path}: {stat_error}")
                last_modified = None
                file_size = 0
            
            return {
                "file_path": file_path,
                "relative_path": relative_path,
                "contributors": list(contributors),
                "blame_data": blame_data,
                "commit_history": commit_history,
                "primary_author": self._get_primary_author(blame_data),
                "last_modified": last_modified.isoformat() if last_modified else None,
                "file_size": file_size,
                "total_commits": len(commit_history)
            }
            
        except Exception as e:
            logger.error(f"File authorship analysis failed for {file_path}: {e}")
            return {"error": f"Authorship analysis failed: {e}"}
    
    def _get_primary_author(self, blame_data: List[Dict[str, Any]]) -> Optional[str]:
        """
        Determine the primary author based on line contributions.
        """
        if not blame_data:
            return None
        
        author_lines = defaultdict(int)
        for blame_entry in blame_data:
            author_lines[blame_entry["author_name"]] += blame_entry["lines"]
        
        if author_lines:
            return max(author_lines, key=author_lines.get)
        return None
    
    def analyze_code_ownership(self, file_extensions: List[str] = None) -> Dict[str, Any]:
        """
        Analyze code ownership patterns across the repository.
        """
        if not self.repo:
            return {"error": "No repository initialized"}
        
        if file_extensions is None:
            file_extensions = ['.py', '.js', '.ts', '.java', '.c', '.cpp', '.h', '.go', '.rs']
        
        try:
            ownership_data = {}
            author_stats = defaultdict(lambda: {
                'files_owned': 0,
                'lines_contributed': 0,
                'commits': 0,
                'languages': set()
            })
            
            # Walk through repository files
            for root, dirs, files in os.walk(self.repo_path):
                # Skip .git directory
                if '.git' in dirs:
                    dirs.remove('.git')
                
                for file in files:
                    file_path = os.path.join(root, file)
                    file_ext = Path(file_path).suffix.lower()
                    
                    if file_ext in file_extensions:
                        authorship = self.get_file_authorship(file_path)
                        
                        if "error" not in authorship and authorship.get("primary_author"):
                            primary_author = authorship["primary_author"]
                            relative_path = authorship["relative_path"]
                            
                            ownership_data[relative_path] = {
                                "primary_author": primary_author,
                                "contributors": authorship["contributors"],
                                "total_commits": authorship["total_commits"],
                                "language": file_ext
                            }
                            
                            # Update author statistics
                            author_stats[primary_author]['files_owned'] += 1
                            author_stats[primary_author]['languages'].add(file_ext)
                            
                            # Count lines from blame data
                            for blame_entry in authorship.get("blame_data", []):
                                author_name = blame_entry["author_name"]
                                author_stats[author_name]['lines_contributed'] += blame_entry["lines"]
            
            # Convert sets to lists for JSON serialization
            for author, stats in author_stats.items():
                stats['languages'] = list(stats['languages'])
            
            return {
                "ownership_data": ownership_data,
                "author_statistics": dict(author_stats),
                "total_files_analyzed": len(ownership_data),
                "supported_extensions": file_extensions
            }
            
        except Exception as e:
            logger.error(f"Code ownership analysis failed: {e}")
            return {"error": f"Ownership analysis failed: {e}"}
    
    def analyze_repository_activity(self, days_back: int = 90) -> Dict[str, Any]:
        """
        Analyze recent repository activity and collaboration patterns.
        """
        if not self.repo:
            return {"error": "No repository initialized"}
        
        try:
            since_date = datetime.now() - timedelta(days=days_back)
            
            # Get recent commits
            recent_commits = []
            author_activity = defaultdict(lambda: {
                'commits': 0,
                'files_changed': 0,
                'insertions': 0,
                'deletions': 0
            })
            
            try:
                commits = list(self.repo.iter_commits(since=since_date, max_count=1000))
                
                for commit in commits:
                    commit_data = {
                        "hash": commit.hexsha,
                        "author_name": commit.author.name,
                        "author_email": commit.author.email,
                        "date": commit.authored_datetime.isoformat(),
                        "message": commit.message.strip(),
                        "files_changed": commit.stats.total['files'],
                        "insertions": commit.stats.total['insertions'],
                        "deletions": commit.stats.total['deletions']
                    }
                    recent_commits.append(commit_data)
                    
                    # Update author activity
                    author = commit.author.name
                    author_activity[author]['commits'] += 1
                    author_activity[author]['files_changed'] += commit.stats.total['files']
                    author_activity[author]['insertions'] += commit.stats.total['insertions']
                    author_activity[author]['deletions'] += commit.stats.total['deletions']
                    
            except Exception as commits_error:
                logger.warning(f"Recent commits analysis failed: {commits_error}")
            
            # Analyze collaboration patterns
            collaboration_matrix = self._analyze_collaboration_patterns(recent_commits)
            
            # Get branch information
            branches = []
            try:
                for branch in self.repo.branches:
                    branches.append({
                        "name": branch.name,
                        "is_active": branch == self.repo.active_branch,
                        "last_commit": branch.commit.hexsha,
                        "last_commit_date": branch.commit.authored_datetime.isoformat()
                    })
            except Exception as branch_error:
                logger.warning(f"Branch analysis failed: {branch_error}")
            
            return {
                "analysis_period_days": days_back,
                "recent_commits": recent_commits[:50],  # Limit for response size
                "total_commits": len(recent_commits),
                "author_activity": dict(author_activity),
                "collaboration_matrix": collaboration_matrix,
                "branches": branches,
                "most_active_authors": self._get_most_active_authors(author_activity)
            }
            
        except Exception as e:
            logger.error(f"Repository activity analysis failed: {e}")
            return {"error": f"Activity analysis failed: {e}"}
    
    def _analyze_collaboration_patterns(self, commits: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze collaboration patterns between authors.
        """
        file_authors = defaultdict(set)
        
        # Build file-author mapping
        for commit in commits:
            author = commit["author_name"]
            try:
                commit_obj = self.repo.commit(commit["hash"])
                for file_path in commit_obj.stats.files:
                    file_authors[file_path].add(author)
            except Exception as e:
                logger.debug(f"Failed to get file stats for commit {commit['hash']}: {e}")
        
        # Calculate collaboration matrix
        author_pairs = defaultdict(int)
        for file_path, authors in file_authors.items():
            if len(authors) > 1:
                author_list = list(authors)
                for i in range(len(author_list)):
                    for j in range(i + 1, len(author_list)):
                        pair = tuple(sorted([author_list[i], author_list[j]]))
                        author_pairs[pair] += 1
        
        return {
            "collaborative_files": len([f for f, authors in file_authors.items() if len(authors) > 1]),
            "author_pairs": dict(author_pairs),
            "total_files": len(file_authors)
        }
    
    def _get_most_active_authors(self, author_activity: Dict[str, Dict[str, int]], limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get most active authors sorted by commit count.
        """
        sorted_authors = sorted(
            author_activity.items(),
            key=lambda x: x[1]['commits'],
            reverse=True
        )
        
        return [
            {
                "author": author,
                "stats": stats
            }
            for author, stats in sorted_authors[:limit]
        ]
    
    def get_developer_expertise(self, author_name: str) -> Dict[str, Any]:
        """
        Get detailed expertise profile for a specific developer.
        """
        if not self.repo:
            return {"error": "No repository initialized"}
        
        try:
            author_files = []
            languages = set()
            total_commits = 0
            
            # Analyze commits by this author
            commits = list(self.repo.iter_commits(author=author_name, max_count=500))
            
            for commit in commits:
                total_commits += 1
                try:
                    for file_path in commit.stats.files:
                        file_ext = Path(file_path).suffix.lower()
                        if file_ext:
                            languages.add(file_ext)
                            
                        author_files.append({
                            "file_path": file_path,
                            "commit_hash": commit.hexsha,
                            "date": commit.authored_datetime.isoformat(),
                            "language": file_ext
                        })
                except Exception as e:
                    logger.debug(f"Failed to analyze commit {commit.hexsha}: {e}")
            
            # Count expertise by language
            language_expertise = Counter()
            for file_info in author_files:
                if file_info["language"]:
                    language_expertise[file_info["language"]] += 1
            
            return {
                "author_name": author_name,
                "total_commits": total_commits,
                "languages": list(languages),
                "language_expertise": dict(language_expertise),
                "files_touched": len(author_files),
                "unique_files": len(set(f["file_path"] for f in author_files)),
                "primary_language": language_expertise.most_common(1)[0][0] if language_expertise else None
            }
            
        except Exception as e:
            logger.error(f"Developer expertise analysis failed for {author_name}: {e}")
            return {"error": f"Expertise analysis failed: {e}"}
    
    def get_repository_summary(self) -> Dict[str, Any]:
        """
        Get high-level repository summary statistics.
        """
        if not self.repo:
            return {"error": "No repository initialized"}
        
        try:
            # Basic repository information
            summary = {
                "repository_path": self.repo_path,
                "active_branch": self.repo.active_branch.name if self.repo.active_branch else "unknown",
                "total_branches": len(list(self.repo.branches)),
                "total_tags": len(list(self.repo.tags))
            }
            
            # Commit statistics
            try:
                commits = list(self.repo.iter_commits(max_count=1000))
                summary.update({
                    "total_commits_analyzed": len(commits),
                    "unique_authors": len(set(commit.author.name for commit in commits)),
                    "first_commit_date": min(commit.authored_datetime for commit in commits).isoformat() if commits else None,
                    "last_commit_date": max(commit.authored_datetime for commit in commits).isoformat() if commits else None
                })
            except Exception as e:
                logger.warning(f"Commit statistics failed: {e}")
                summary.update({
                    "total_commits_analyzed": 0,
                    "unique_authors": 0,
                    "first_commit_date": None,
                    "last_commit_date": None
                })
            
            # File statistics
            file_count = 0
            tracked_extensions = set()
            
            try:
                for root, dirs, files in os.walk(self.repo_path):
                    if '.git' in dirs:
                        dirs.remove('.git')
                    
                    for file in files:
                        file_count += 1
                        file_ext = Path(file).suffix.lower()
                        if file_ext:
                            tracked_extensions.add(file_ext)
                
                summary.update({
                    "total_files": file_count,
                    "file_extensions": list(tracked_extensions)
                })
            except Exception as e:
                logger.warning(f"File statistics failed: {e}")
                summary.update({
                    "total_files": 0,
                    "file_extensions": []
                })
            
            return summary
            
        except Exception as e:
            logger.error(f"Repository summary failed: {e}")
            return {"error": f"Summary generation failed: {e}"}
    
    def is_git_repository(self, path: str) -> bool:
        """
        Check if the given path contains a Git repository.
        """
        try:
            git.Repo(path)
            return True
        except (GitCommandError, InvalidGitRepositoryError):
            return False
    
    def get_current_repository(self) -> Optional[str]:
        """
        Get the path of the currently initialized repository.
        """
        return self.repo_path if self.repo else None