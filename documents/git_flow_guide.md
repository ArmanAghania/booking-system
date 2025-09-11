# Git Flow Workflow Guide

This document provides a comprehensive guide for using Git Flow in the booking system project.

## Table of Contents

1. [What is Git Flow?](#what-is-git-flow)
2. [Branch Structure](#branch-structure)
3. [Git Flow Commands](#git-flow-commands)
4. [Workflow Examples](#workflow-examples)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

## What is Git Flow?

Git Flow is a branching model that defines a strict branching structure designed around project releases. It provides a robust framework for managing features, releases, and hotfixes in a collaborative environment.

### Benefits of Git Flow

- **Clear separation** between development and production code
- **Structured release process** with proper testing and integration
- **Parallel development** of multiple features
- **Emergency hotfixes** without disrupting ongoing development
- **Version tracking** with semantic versioning

## Branch Structure

Our Git Flow setup uses the following branch structure:

```
main (production)
├── develop (integration)
│   ├── feature/user-authentication
│   ├── feature/appointment-booking
│   └── bugfix/login-validation
├── release/v1.0.0
└── hotfix/critical-security-fix
```

### Branch Types

| Branch Type | Purpose | Base Branch | Merge Target |
|-------------|---------|-------------|--------------|
| `main` | Production-ready code | - | - |
| `develop` | Integration branch for features | `main` | `main` (via release) |
| `feature/*` | New features and enhancements | `develop` | `develop` |
| `bugfix/*` | Bug fixes for develop branch | `develop` | `develop` |
| `release/*` | Release preparation | `develop` | `main` + `develop` |
| `hotfix/*` | Critical production fixes | `main` | `main` + `develop` |

## Git Flow Commands

### Initial Setup

```bash
# Initialize Git Flow in your repository
git flow init

# Configure branch names (if different from defaults)
# Production releases: main
# Development: develop
# Feature prefix: feature/
# Bugfix prefix: bugfix/
# Release prefix: release/
# Hotfix prefix: hotfix/
# Version tag prefix: v
```

### Feature Development

#### Starting a New Feature

```bash
# Start a new feature
git flow feature start feature-name

# Example: Start user authentication feature
git flow feature start user-authentication
```

This command:
- Creates a new branch `feature/feature-name` from `develop`
- Switches to the new feature branch
- Sets up tracking with the remote

#### Working on a Feature

```bash
# Make your changes
git add .
git commit -m "Add user login functionality"

# Push feature branch to remote
git push origin feature/feature-name

# Continue making commits as needed
git add .
git commit -m "Add password validation"
git push origin feature/feature-name
```

#### Finishing a Feature

```bash
# Finish the feature (merges to develop and deletes feature branch)
git flow feature finish feature-name

# Push the updated develop branch
git push origin develop
```

This command:
- Merges the feature branch into `develop`
- Deletes the local feature branch
- Switches back to `develop`

### Bug Fixes

#### Starting a Bug Fix

```bash
# Start a bug fix
git flow bugfix start bugfix-name

# Example: Fix appointment validation bug
git flow bugfix start appointment-validation-fix
```

#### Finishing a Bug Fix

```bash
# Finish the bug fix
git flow bugfix finish bugfix-name

# Push the updated develop branch
git push origin develop
```

### Release Management

#### Starting a Release

```bash
# Start a new release
git flow release start 1.0.0

# This creates release/1.0.0 branch from develop
```

#### Release Preparation

```bash
# Make any final adjustments
# Update version numbers, changelog, etc.
git add .
git commit -m "Update version to 1.0.0"

# Push release branch
git push origin release/1.0.0
```

#### Finishing a Release

```bash
# Finish the release
git flow release finish 1.0.0

# Push all changes
git push origin main
git push origin develop
git push --tags
```

This command:
- Merges release branch into `main`
- Tags the release with `v1.0.0`
- Merges release branch back into `develop`
- Deletes the release branch

### Hotfixes

#### Starting a Hotfix

```bash
# Start a hotfix for production
git flow hotfix start 1.0.1

# This creates hotfix/1.0.1 branch from main
```

#### Finishing a Hotfix

```bash
# Make critical fixes
git add .
git commit -m "Fix critical security vulnerability"

# Finish the hotfix
git flow hotfix finish 1.0.1

# Push all changes
git push origin main
git push origin develop
git push --tags
```

This command:
- Merges hotfix into `main`
- Tags the hotfix with `v1.0.1`
- Merges hotfix into `develop`
- Deletes the hotfix branch

## Workflow Examples

### Example 1: Adding a New Feature

```bash
# 1. Start feature
git flow feature start appointment-reminders

# 2. Develop the feature
git add .
git commit -m "Add email reminder system"
git push origin feature/appointment-reminders

# 3. Continue development
git add .
git commit -m "Add SMS reminder option"
git push origin feature/appointment-reminders

# 4. Create pull request on GitHub
# Target: develop branch

# 5. After PR approval and merge
git checkout develop
git pull origin develop
git branch -d feature/appointment-reminders
```

### Example 2: Creating a Release

```bash
# 1. Start release
git flow release start 1.1.0

# 2. Update version files
echo "1.1.0" > VERSION
git add VERSION
git commit -m "Bump version to 1.1.0"

# 3. Update changelog
git add CHANGELOG.md
git commit -m "Update changelog for v1.1.0"

# 4. Push release branch
git push origin release/1.1.0

# 5. Create release PR on GitHub
# Target: main branch

# 6. After PR approval and merge
git flow release finish 1.1.0
git push origin main
git push origin develop
git push --tags
```

### Example 3: Emergency Hotfix

```bash
# 1. Start hotfix
git flow hotfix start 1.0.1

# 2. Make critical fix
git add .
git commit -m "Fix payment processing bug"

# 3. Push hotfix branch
git push origin hotfix/1.0.1

# 4. Create hotfix PR on GitHub
# Target: main branch

# 5. After PR approval and merge
git flow hotfix finish 1.0.1
git push origin main
git push origin develop
git push --tags
```

## Best Practices

### Branch Naming

- **Features**: `feature/descriptive-name`
  - ✅ `feature/user-authentication`
  - ✅ `feature/appointment-booking`
  - ❌ `feature/fix` (too vague)

- **Bugfixes**: `bugfix/descriptive-name`
  - ✅ `bugfix/login-validation-error`
  - ✅ `bugfix/payment-processing-fix`
  - ❌ `bugfix/bug` (too vague)

- **Releases**: `release/version-number`
  - ✅ `release/1.0.0`
  - ✅ `release/2.1.0`
  - ❌ `release/v1.0.0` (version tag prefix is handled automatically)

- **Hotfixes**: `hotfix/version-number`
  - ✅ `hotfix/1.0.1`
  - ✅ `hotfix/2.1.1`

### Commit Messages

Follow conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

Examples:
- `feat(auth): add OAuth2 login support`
- `fix(payments): resolve currency conversion bug`
- `docs(readme): update installation instructions`
- `refactor(api): simplify appointment booking logic`

### Pull Request Guidelines

1. **Target the correct branch**:
   - Features → `develop`
   - Releases → `main`
   - Hotfixes → `main`

2. **Write descriptive PR titles and descriptions**

3. **Link related issues** using `Fixes #123` or `Closes #456`

4. **Request appropriate reviewers**

5. **Ensure all tests pass**

### Version Numbering

Use [Semantic Versioning](https://semver.org/):

- **MAJOR** (1.0.0): Breaking changes
- **MINOR** (0.1.0): New features, backward compatible
- **PATCH** (0.0.1): Bug fixes, backward compatible

Examples:
- `1.0.0` - Initial release
- `1.1.0` - Added new features
- `1.1.1` - Bug fixes
- `2.0.0` - Breaking changes

## Troubleshooting

### Common Issues

#### 1. Feature Branch Already Exists

```bash
# Error: Branch 'feature/name' already exists
# Solution: Use a different name or delete the existing branch
git branch -D feature/name
git flow feature start name
```

#### 2. Merge Conflicts

```bash
# Resolve conflicts manually
git status
# Edit conflicted files
git add .
git commit -m "Resolve merge conflicts"
```

#### 3. Accidentally Deleted Branch

```bash
# Recover from remote
git fetch origin
git checkout -b feature/name origin/feature/name
```

#### 4. Wrong Base Branch

```bash
# If you started from wrong branch
git checkout feature/name
git rebase develop
# Resolve conflicts if any
git push --force-with-lease origin feature/name
```

### Git Flow Not Installed

#### Install Git Flow

**Ubuntu/Debian:**
```bash
sudo apt install git-flow
```

**macOS:**
```bash
brew install git-flow-avh
```

**Windows:**
```bash
# Using Git for Windows (comes with Git Flow)
# Or install Git Flow AVH Edition
```

### Useful Commands

```bash
# Check Git Flow status
git flow

# List all branches
git branch -a

# Check current branch
git branch

# View commit history
git log --oneline --graph --all

# Clean up merged branches
git branch --merged | grep -v "\*\|main\|develop" | xargs -n 1 git branch -d
```

## Integration with GitHub

### Branch Protection Rules

Set up branch protection for:
- `main` branch: Require PR reviews, require status checks
- `develop` branch: Require PR reviews, require status checks

### Pull Request Templates

Create `.github/pull_request_template.md`:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
```

### GitHub Actions

Example workflow for automated testing:

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [develop, main]
  pull_request:
    branches: [develop, main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python manage.py test
```

## Resources

- [Git Flow Documentation](https://github.com/nvie/gitflow)
- [Atlassian Git Flow Tutorial](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow)
- [Semantic Versioning](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
