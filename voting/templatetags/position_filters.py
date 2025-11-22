from django import template

register = template.Library()

@register.filter
def clean_position_name(name):
    """Remove common position words from the name."""
    if not name:
        return name
        
    # List of words to remove (case insensitive)
    words_to_remove = ['president', 'v-president', 'vice president', 'secretary']
    
    # Split the name into words and filter out the ones we want to remove
    cleaned_words = [
        word for word in name.split() 
        if word.lower() not in [w.lower() for w in words_to_remove]
    ]
    
    # Join the remaining words back together
    return ' '.join(cleaned_words).strip() or name
