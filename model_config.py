# Shared configuration for model training and inference
# These settings must be identical between train_model.py and run_consultant.py

# Features to exclude from training (in addition to 'page' URL and target)
# These are typically metrics that are outcomes rather than causes, or highly correlated with the target
FEATURES_TO_EXCLUDE = [
    'FirstMeaningfulPaint',
    'FirstImagePaint', 
    'FirstContentfulPaint',
    'LargestContentfulPaint'
]

# Categorical Features Configuration
# These columns will be treated as categories by LightGBM
# Good candidates have few unique values (e.g., booleans, or counts from 0-50)
MANUAL_CATEGORICAL_FEATURES = [
    'uses_cdn',              # Boolean (2 values)
    'reqCss',                # 0-41 CSS requests
    'reqFont',               # 0-38 font requests
    'reqJS',                 # JavaScript requests
    'renderBlockingCSS',     # 0-23 render blocking CSS (fixed name)
    'renderBlockingJS',      # 0-34 render blocking JS (fixed name)
    'num_long_tasks',        # 1-67 long tasks
    'analytics',             # 0-7 analytics scripts
    'ads',                   # 0-15 ad scripts
    'marketing',             # 0-2 marketing scripts
    'fonts_scripts',         # 0-3 font scripts
    'tagman',                # 0-2 tag manager scripts
    'chat',                  # 0-2 chat scripts
    '_responses_404',        # 0-8 404 responses
    'is_lcp_preloaded',      # Boolean for LCP preload
    'scripts_defer',         # 0-50 deferred scripts
    'scripts_async',         # Async scripts (likely similar range)
    'scripts_inline'         # Inline scripts (likely similar range)
]

