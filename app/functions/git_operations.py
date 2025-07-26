"""
Git operations functions for version control commands.
All functions return strings as they will be passed to the AI agent.
"""

import subprocess
import os
from pathlib import Path
from typing import List, Dict, Any


def check_git_repository(project_root: str = None) -> str:
    """
    Check if current directory is a git repository.
    
    Args:
        project_root: Project root directory (uses current dir if None)
        
    Returns:
        String with git repository status
    """
    try:
        if project_root:
            os.chdir(project_root)
            
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            # Get repository info
            repo_info = subprocess.run(
                ["git", "remote", "-v"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            branch_info = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            current_branch = branch_info.stdout.strip() if branch_info.returncode == 0 else "unknown"
            remote_info = repo_info.stdout.strip() if repo_info.returncode == 0 else "No remotes"
            
            return f"✅ Git repository detected\nCurrent branch: {current_branch}\nRemotes:\n{remote_info}"
        else:
            return "❌ Not a git repository. Run 'git init' to initialize one."
            
    except subprocess.TimeoutExpired:
        return "❌ Git command timed out"
    except FileNotFoundError:
        return "❌ Git not found. Please install git first."
    except Exception as e:
        return f"❌ Error checking git repository: {str(e)}"


def get_git_status(project_root: str = None) -> str:
    """
    Get git status including staged and unstaged files.
    
    Args:
        project_root: Project root directory
        
    Returns:
        String with git status information
    """
    try:
        if project_root:
            os.chdir(project_root)
            
        # Check if it's a git repo first
        repo_check = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if repo_check.returncode != 0:
            return "❌ Not a git repository"
            
        # Get git status
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return f"❌ Git status failed: {result.stderr}"
            
        status_lines = result.stdout.strip().split('\n')
        
        if not status_lines or status_lines == ['']:
            return "✅ Working directory clean - no changes to commit"
            
        staged_files = []
        unstaged_files = []
        untracked_files = []
        
        for line in status_lines:
            if len(line) < 3:
                continue
                
            status_code = line[:2]
            filename = line[3:]
            
            # Parse git status codes
            staged_status = status_code[0]
            unstaged_status = status_code[1]
            
            if staged_status != ' ' and staged_status != '?':
                staged_files.append(f"{staged_status} {filename}")
            
            if unstaged_status == 'M':
                unstaged_files.append(f"M {filename}")
            elif unstaged_status == 'D':
                unstaged_files.append(f"D {filename}")
            elif status_code == '??':
                untracked_files.append(f"? {filename}")
                
        # Format output
        output = "📋 Git Status Summary:\n" + "="*30 + "\n"
        
        if staged_files:
            output += f"\n✅ Staged files ({len(staged_files)}):\n"
            for file in staged_files:
                output += f"  {file}\n"
        
        if unstaged_files:
            output += f"\n⚠️  Unstaged changes ({len(unstaged_files)}):\n"
            for file in unstaged_files:
                output += f"  {file}\n"
                
        if untracked_files:
            output += f"\n❓ Untracked files ({len(untracked_files)}):\n"
            for file in untracked_files[:5]:  # Limit to first 5
                output += f"  {file}\n"
            if len(untracked_files) > 5:
                output += f"  ... and {len(untracked_files) - 5} more\n"
        
        return output
        
    except subprocess.TimeoutExpired:
        return "❌ Git status command timed out"
    except Exception as e:
        return f"❌ Error getting git status: {str(e)}"


def get_staged_files() -> str:
    """
    Get list of staged files ready for commit.
    
    Returns:
        String with staged files information
    """
    try:
        # Check if it's a git repo first
        repo_check = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if repo_check.returncode != 0:
            return "❌ Not a git repository"
            
        # Get staged files
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-status"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return f"❌ Git diff failed: {result.stderr}"
            
        staged_lines = result.stdout.strip().split('\n')
        
        if not staged_lines or staged_lines == ['']:
            return "❌ No files in staging area. Use 'git add <files>' to stage files for commit."
            
        output = "📦 Files ready for commit:\n" + "="*30 + "\n"
        
        for line in staged_lines:
            if line.strip():
                parts = line.split('\t')
                if len(parts) >= 2:
                    status = parts[0]
                    filename = parts[1]
                    
                    status_desc = {
                        'A': '➕ Added',
                        'M': '📝 Modified', 
                        'D': '🗑️  Deleted',
                        'R': '🔄 Renamed',
                        'C': '📋 Copied'
                    }.get(status, f'❓ {status}')
                    
                    output += f"  {status_desc}: {filename}\n"
        
        return output
        
    except subprocess.TimeoutExpired:
        return "❌ Git diff command timed out"
    except Exception as e:
        return f"❌ Error getting staged files: {str(e)}"


def get_staged_diff() -> str:
    """
    Get the diff of staged changes for AI analysis.
    
    Returns:
        String with staged diff content
    """
    try:
        # Get staged diff
        result = subprocess.run(
            ["git", "diff", "--cached"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return f"❌ Git diff failed: {result.stderr}"
            
        diff_content = result.stdout.strip()
        
        if not diff_content:
            return "❌ No staged changes found"
            
        # Limit diff size for AI processing
        if len(diff_content) > 5000:
            lines = diff_content.split('\n')
            limited_diff = '\n'.join(lines[:100])  # First 100 lines
            return f"{limited_diff}\n\n... (diff truncated for AI analysis)"
        
        return diff_content
        
    except subprocess.TimeoutExpired:
        return "❌ Git diff command timed out"
    except Exception as e:
        return f"❌ Error getting staged diff: {str(e)}"


def execute_git_commit(commit_message: str) -> str:
    """
    Execute git commit with the provided message.
    
    Args:
        commit_message: The commit message to use
        
    Returns:
        String with commit result
    """
    try:
        # Check if there are staged files
        staged_check = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            capture_output=True,
            timeout=10
        )
        
        if staged_check.returncode == 0:
            return "❌ No staged changes to commit"
            
        # Execute commit
        result = subprocess.run(
            ["git", "commit", "-m", commit_message],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            # Get commit hash
            hash_result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            commit_hash = hash_result.stdout.strip() if hash_result.returncode == 0 else "unknown"
            
            return f"✅ Commit successful!\nCommit hash: {commit_hash}\n\nCommit details:\n{result.stdout}"
        else:
            return f"❌ Commit failed: {result.stderr}"
            
    except subprocess.TimeoutExpired:
        return "❌ Git commit command timed out"
    except Exception as e:
        return f"❌ Error executing commit: {str(e)}"


def get_recent_commits(count: int = 5) -> str:
    """
    Get recent commit history for context.
    
    Args:
        count: Number of recent commits to show
        
    Returns:
        String with recent commit history
    """
    try:
        result = subprocess.run(
            ["git", "log", f"-{count}", "--oneline", "--decorate"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            commits = result.stdout.strip()
            if commits:
                return f"📝 Recent commits:\n{commits}"
            else:
                return "📝 No commit history found"
        else:
            return "❌ Could not retrieve commit history"
            
    except subprocess.TimeoutExpired:
        return "❌ Git log command timed out"
    except Exception as e:
        return f"❌ Error getting commit history: {str(e)}"


def get_all_changes_diff() -> str:
    """
    Get the diff of all changes (staged and unstaged) for code review.
    
    Returns:
        String with complete diff content
    """
    try:
        # Get both staged and unstaged changes
        result = subprocess.run(
            ["git", "diff", "HEAD"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return f"❌ Git diff failed: {result.stderr}"
            
        diff_content = result.stdout.strip()
        
        if not diff_content:
            # Try to get staged changes if no HEAD diff
            staged_result = subprocess.run(
                ["git", "diff", "--cached"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if staged_result.returncode == 0 and staged_result.stdout.strip():
                diff_content = staged_result.stdout.strip()
            else:
                return "❌ No changes found to review"
            
        # Limit diff size for AI processing
        if len(diff_content) > 8000:
            lines = diff_content.split('\n')
            limited_diff = '\n'.join(lines[:150])  # First 150 lines
            return f"{limited_diff}\n\n... (diff truncated for review analysis)"
        
        return diff_content
        
    except subprocess.TimeoutExpired:
        return "❌ Git diff command timed out"
    except Exception as e:
        return f"❌ Error getting changes diff: {str(e)}"