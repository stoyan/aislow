# Friendly name lookup table for features
# Maps technical column names to user-friendly display names

FEATURE_NAME_MAP = {
    # Target & Identifier
    'page': "Page URL",
    'SpeedIndex': "Speed Index",
    
    # Resource Sizes (Bytes)
    'totalBytes': "Total Page Size (Bytes)",
    'bytesCss': "CSS Size (Bytes)",
    'bytesJS': "JavaScript Size (Bytes)",
    'bytesImg': "Image Size (Bytes)",
    'bytesFont': "Font Size (Bytes)",
    'bytesHtml': "HTML Size (Bytes)",
    'bytesJSON': "JSON Size (Bytes)",
    'gzipSavings': "Potential Gzip Savings",
    
    # Request Counts
    'reqTotal': "Total Requests (Count)",
    'reqCss': "CSS Requests (Count)",
    'reqJS': "JavaScript Requests (Count)",
    'reqImg': "Image Requests (Count)",
    'reqFont': "Font Requests (Count)",
    'reqHtml': "HTML Requests (Count)",
    'reqJSON': "JSON Requests (Count)",
    
    # Network & Infrastructure
    'TTFB': "Time To First Byte (ms)",
    'numConnections': "TCP Connections (Count)",
    'numDomains': "Unique Domains (Count)",
    'numRedirects': "HTTP Redirects (Count)",
    'uses_cdn': "Uses CDN (Boolean)",
    'maxDomainReqs': "Max Requests Per Domain (Count)",
    
    # Cache Headers
    'maxage0': "No Cache Resources",
    'maxage1': "Cached < 1 Day",
    'maxage30': "Cached 1-30 Days",
    'maxage365': "Cached 30-365 Days",
    'maxageMore': "Cached > 1 Year",
    'maxageNull': "No Cache Header",
    
    # Rendering Metrics
    'renderStart': "Render Start Time",
    'numDomElements': "DOM Element Count",
    'renderBlockingCSS': "Render-Blocking CSS",
    'renderBlockingJS': "Render-Blocking JavaScript",
    
    # Core Web Vitals & Paint Metrics
    'FirstPaint': "First Paint",
    'FirstContentfulPaint': "First Contentful Paint",
    'FirstImagePaint': "First Image Paint",
    'FirstMeaningfulPaint': "First Meaningful Paint",
    'LargestContentfulPaint': "Largest Contentful Paint",
    'layout_shifts_count': "Layout Shifts Count",
    
    # Performance Issues
    'num_long_tasks': "Long Tasks Count",
    'TotalBlockingTime': "Total Blocking Time",
    'EvaluateScript': "Script Evaluation Time",
    'FunctionCall': "Function Call Time",
    'Layout': "Layout Calculation Time",
    
    # Image Optimization
    'image_savings': "Potential Image Savings",
    'img_missing_width': "Images Missing Width",
    'img_missing_height': "Images Missing Height",
    'img_lazy_count': "Lazy Loaded Images",
    'svg_count': "SVG Images",
    
    # Script Loading Strategies
    'scripts_total': "Total Scripts",
    'scripts_inline': "Inline Scripts",
    'scripts_async': "Async Scripts",
    'scripts_defer': "Deferred Scripts",
    'is_lcp_preloaded': "LCP Resource Preloaded",
    
    # Third-Party Categories
    'analytics': "Analytics Scripts",
    'ads': "Advertising Scripts",
    'marketing': "Marketing Scripts",
    'fonts_scripts': "Font Loading Scripts",
    'tagman': "Tag Manager Scripts",
    'chat': "Chat Widget Scripts",
    
    # HTTP Responses
    '_responses_200': "Successful Responses (200)",
    '_responses_404': "Not Found Errors (404)",
    '_responses_other': "Other HTTP Responses",
    
    # Loading Events
    'loadEventDuration': "Load Event Duration",
    'dclDuration': "DOMContentLoaded Duration",
}

