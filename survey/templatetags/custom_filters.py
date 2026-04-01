from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """الحصول على قيمة من القاموس باستخدام المفتاح"""
    if dictionary is None:
        return None
    key_str = f'question_{key}'
    return dictionary.get(key_str)
