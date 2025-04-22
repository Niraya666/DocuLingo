import re

# (REMOVE <SCRIPT> to </script> and variations)
SCRIPT_PATTERN = r'<[ ]*script.*?\/[ ]*script[ ]*>'  # mach any char zero or more times
# text = re.sub(pattern, '', text, flags=(re.IGNORECASE | re.MULTILINE | re.DOTALL))

# (REMOVE HTML <STYLE> to </style> and variations)
STYLE_PATTERN = r'<[ ]*style.*?\/[ ]*style[ ]*>'  # mach any char zero or more times
# text = re.sub(pattern, '', text, flags=(re.IGNORECASE | re.MULTILINE | re.DOTALL))

# (REMOVE HTML <META> to </meta> and variations)
META_PATTERN = r'<[ ]*meta.*?>'  # mach any char zero or more times
# text = re.sub(pattern, '', text, flags=(re.IGNORECASE | re.MULTILINE | re.DOTALL))

# (REMOVE HTML COMMENTS <!-- to --> and variations)
COMMENT_PATTERN = r'<[ ]*!--.*?--[ ]*>'  # mach any char zero or more times
# text = re.sub(pattern, '', text, flags=(re.IGNORECASE | re.MULTILINE | re.DOTALL))

# (REMOVE HTML LINK <LINK> to </link> and variations)
LINK_PATTERN = r'<[ ]*link.*?>'  # mach any char zero or more times

# (REPLACE base64 images)
BASE64_IMG_PATTERN = r'<img[^>]+src="data:image/[^;]+;base64,[^"]+"[^>]*>'

# (REPLACE <svg> to </svg> and variations)
SVG_PATTERN = r'(<svg[^>]*>)(.*?)(<\/svg>)'
def replace_svg(html: str, new_content: str = "this is a placeholder") -> str:
    return re.sub(
        SVG_PATTERN,
        lambda match: f"{match.group(1)}{new_content}{match.group(3)}",
        html,
        flags=re.DOTALL,
    )


def replace_base64_images(html: str, new_image_src: str = "#") -> str:
    return re.sub(BASE64_IMG_PATTERN, f'<img src="{new_image_src}"/>', html)


def has_base64_images(text: str) -> bool:
    base64_content_pattern = r'data:image/[^;]+;base64,[^"]+'
    return bool(re.search(base64_content_pattern, text, flags=re.DOTALL))


def has_svg_components(text: str) -> bool:
    return bool(re.search(SVG_PATTERN, text, flags=re.DOTALL))
    
def html_cleaning(html: str, clean_svg: bool = False, clean_base64: bool = False):
    


    
        
    html = re.sub(SCRIPT_PATTERN, '', html, flags=(re.IGNORECASE | re.MULTILINE | re.DOTALL))
    html = re.sub(STYLE_PATTERN, '', html, flags=(re.IGNORECASE | re.MULTILINE | re.DOTALL))
    html = re.sub(META_PATTERN, '', html, flags=(re.IGNORECASE | re.MULTILINE | re.DOTALL))
    html = re.sub(COMMENT_PATTERN, '', html, flags=(re.IGNORECASE | re.MULTILINE | re.DOTALL))
    html = re.sub(LINK_PATTERN, '', html, flags=(re.IGNORECASE | re.MULTILINE | re.DOTALL))

    if clean_svg:
        html = replace_svg(html)

    if clean_base64:
        html = replace_base64_images(html)

    return html