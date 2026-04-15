"""Manual input validation — no DRF, as required."""


def validate_prompt_create(data):
    errors = {}

    title = data.get('title', '').strip()
    if not title:
        errors['title'] = 'Title is required.'
    elif len(title) < 3:
        errors['title'] = 'Title must be at least 3 characters.'
    elif len(title) > 255:
        errors['title'] = 'Title cannot exceed 255 characters.'

    content = data.get('content', '').strip()
    if not content:
        errors['content'] = 'Content is required.'
    elif len(content) < 20:
        errors['content'] = 'Content must be at least 20 characters.'

    complexity = data.get('complexity')
    if complexity is None:
        errors['complexity'] = 'Complexity is required.'
    else:
        try:
            complexity = int(complexity)
            if not (1 <= complexity <= 10):
                errors['complexity'] = 'Complexity must be between 1 and 10.'
        except (ValueError, TypeError):
            errors['complexity'] = 'Complexity must be an integer between 1 and 10.'

    tags = data.get('tags', [])
    if not isinstance(tags, list):
        errors['tags'] = 'Tags must be a list of strings.'
    elif len(tags) > 10:
        errors['tags'] = 'Maximum 10 tags allowed.'
    else:
        for tag in tags:
            if not isinstance(tag, str) or len(tag.strip()) == 0:
                errors['tags'] = 'Each tag must be a non-empty string.'
                break
            if len(tag) > 50:
                errors['tags'] = 'Each tag cannot exceed 50 characters.'
                break

    return errors


def validate_prompt_update(data):
    errors = {}

    if 'title' in data:
        title = data.get('title', '').strip()
        if len(title) < 3:
            errors['title'] = 'Title must be at least 3 characters.'
        elif len(title) > 255:
            errors['title'] = 'Title cannot exceed 255 characters.'

    if 'content' in data:
        content = data.get('content', '').strip()
        if len(content) < 20:
            errors['content'] = 'Content must be at least 20 characters.'

    if 'complexity' in data:
        try:
            complexity = int(data['complexity'])
            if not (1 <= complexity <= 10):
                errors['complexity'] = 'Complexity must be between 1 and 10.'
        except (ValueError, TypeError):
            errors['complexity'] = 'Complexity must be an integer between 1 and 10.'

    return errors
