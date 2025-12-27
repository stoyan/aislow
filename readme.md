# AI Web Performance Consultant

Writeup here: https://calendar.perfplanet.com/2025/aislow/

This project builds an AI model that acts as a "virtual performance consultant." It analyzes web performance data (`results.json`) to identify the most significant factors hurting a page's `SpeedIndex` and provides actionable, data-driven recommendations.

The core idea is not to *predict* a `SpeedIndex` but to **explain why** a page's `SpeedIndex` is what it is.

## 1. Data Strategy

### Target Metric
* **`SpeedIndex`**: The primary target metric we are training the model to understand.

### Training Data
* **Source:** HTTP Archive on BigQuery.
* **High Contrast Dataset:** polarized dataset to teach the model the clear difference between "perfect" and "broken" pages. The training set should be built by combining fastest and slowest pages, yet chopping off the very slow (SI > 20K ms) and very fast (SI <500ms) to avoid error pages and near-timeouts. We also favor popular pages (based on the `rank` column in BQ)
* **Why:** This polarized dataset gives the model strong "high contrast" signals. It learns the clear patterns of what *causes* a page to be slow, rather than just learning what an "average" page looks like. This makes its explanations (SHAP values) much more confident and accurate.

### Data Queried

* fast pages with SI between 500 and 2500 and rank under 10K (lower = popular), we select all of these in the archive, about 6000 URLs
* fast pages with SI between 500 and 2500 and rank under 50K, we select a random sample of 5000 URLs
* Slow pages. SI under 20000 to avoid *really* slow pages. And over 4500 (a number inspired by CoreWebVitals). We have a selection of all matching pages with rank under 10K and under 50K and then a random sample of 5K URLs with rank under 100K

This way we have 10K+ fast and 10k+ slow pages, eliminating outliers and erring on the side of popular pages (presumably representing better crafted sites)

### Fields (65 Features)

Our dataset contains 65 fields organized into the following categories:

#### Target & Identifier
* **`page`**: The URL of the page (excluded from training)
* **`SpeedIndex`**: Target metric - measures how quickly content is visually displayed (milliseconds)

#### Resource Sizes (Bytes)
* **`totalBytes`**: Total page weight in bytes
* **`bytesCss`**: Total CSS bytes
* **`bytesJS`**: Total JavaScript bytes
* **`bytesImg`**: Total image bytes
* **`bytesFont`**: Total font bytes
* **`bytesHtml`**: Total HTML bytes
* **`bytesJSON`**: Total JSON bytes
* **`gzipSavings`**: Potential bytes saved if gzip compression applied

#### Request Counts
* **`reqTotal`**: Total number of HTTP requests
* **`reqCss`**: Number of CSS file requests
* **`reqJS`**: Number of JavaScript file requests
* **`reqImg`**: Number of image requests
* **`reqFont`**: Number of font file requests
* **`reqHtml`**: Number of HTML requests
* **`reqJSON`**: Number of JSON requests

#### Network & Infrastructure
* **`TTFB`**: Time To First Byte - server response time (milliseconds)
* **`numConnections`**: Number of TCP connections opened
* **`numDomains`**: Number of unique domains connected to
* **`numRedirects`**: Number of HTTP redirects
* **`uses_cdn`**: Boolean - whether the page uses a CDN
* **`maxDomainReqs`**: Maximum requests to any single domain

#### Cache Headers
* **`maxage0`**: Number of resources with max-age=0 (no cache)
* **`maxage1`**: Number of resources cached for < 1 day
* **`maxage30`**: Number of resources cached between 1 and 30 days
* **`maxage365`**: Number of resources cached between 30 days and a 1 year
* **`maxageMore`**: Number of resources cached for > 1 year
* **`maxageNull`**: Number of resources with no cache header

#### Rendering Metrics
* **`renderStart`**: When rendering started (milliseconds)
* **`numDomElements`**: Total number of DOM elements on the page
* **`renderBlockingCSS`**: Number of render-blocking CSS resources
* **`renderBlockingJS`**: Number of render-blocking JavaScript resources

#### Core Web Vitals & Paint Metrics
* **`FirstPaint`**: Time to first paint (milliseconds)
* **`FirstContentfulPaint`**: FCP - first text/image paint (milliseconds)
* **`FirstImagePaint`**: Time until first image rendered (milliseconds)
* **`FirstMeaningfulPaint`**: FMP - primary content visible (milliseconds)
* **`LargestContentfulPaint`**: LCP - largest content element rendered (milliseconds)
* **`layout_shifts_count`**: Number of layout shifts (CLS-related)

#### Performance Issues
* **`num_long_tasks`**: Number of long tasks (> 50ms) blocking main thread
* **`TotalBlockingTime`**: TBT - sum of blocking time from long tasks (milliseconds)
* **`EvaluateScript`**: Time spent evaluating/parsing JavaScript (milliseconds)
* **`FunctionCall`**: Time spent in JavaScript function calls (milliseconds)
* **`Layout`**: Time spent in layout/reflow calculations (milliseconds)

#### Image Optimization
* **`image_savings`**: Potential bytes saved from image optimization
* **`img_missing_width`**: Number of images without width attribute
* **`img_missing_height`**: Number of images without height attribute
* **`img_lazy_count`**: Number of images with lazy loading
* **`svg_count`**: Number of SVG images

#### Script Loading Strategies
* **`scripts_total`**: Total number of script tags
* **`scripts_inline`**: Number of inline scripts
* **`scripts_async`**: Number of async scripts
* **`scripts_defer`**: Number of deferred scripts
* **`is_lcp_preloaded`**: Boolean - whether LCP resource is preloaded

#### Third-Party Categories
* **`analytics`**: Number of analytics scripts (e.g., Google Analytics)
* **`ads`**: Number of advertising scripts
* **`marketing`**: Number of marketing/tracking scripts
* **`fonts_scripts`**: Number of font loading scripts
* **`tagman`**: Number of tag manager scripts (e.g., GTM)
* **`chat`**: Number of chat widget scripts

#### HTTP Responses
* **`_responses_200`**: Number of successful (200 OK) responses
* **`_responses_404`**: Number of 404 (Not Found) errors
* **`_responses_other`**: Number of other HTTP status codes

#### Loading Events
* **`loadEventDuration`**: Time for the load event to complete (milliseconds)
* **`dclDuration`**: DOMContentLoaded event duration (milliseconds)

## 2. Model & Tooling

### Model Choice: LightGBM
We selected **LightGBM** (`LGBMRegressor`) for several key reasons:

1.  **Task:** We are performing a **Regression** task (predicting a number).
2.  **Why Regression?** Our goal isn't to use the model's *prediction*. Our goal is to train a model that understands the complex relationships between all 50 features and `SpeedIndex`, so we can use SHAP to **explain its reasoning**.
3.  **Why LightGBM?**
    * **State-of-the-Art:** It's a gradient-boosted tree model, which is the industry standard for tabular data (like our CSV).
    * **Fast:** It trained on 10,000 rows in 0.36 seconds.
    * **Lightweight:** The final saved model (`.pkl`) was only 93KB.
    * **SHAP-Friendly:** It works perfectly with `shap.TreeExplainer` for fast, accurate explanations.

We explicitly decided **against** TensorFlow / Deep Learning, as it would be overkill and significantly more difficult to get reliable feature-based explanations.

### Key Python Libraries
* `pandas`: For loading and manipulating the CSV data.
* `lightgbm`: For the core model training.
* `scikit-learn`: For the `train_test_split` function.
* `joblib`: For saving and loading the trained model (`.pkl` file).
* `shap`: For explaining the model's predictions.

## 3. Training Process (`train_model.py`)

1.  **Data Splitting:** We used an **80/20 train/test split**.
    * **Why:** To get an honest grade. The model *learns* on the 80% "training" set and is then *graded* on the 20% "test" set it has never seen. This prevents **overfitting** (memorization) and proves the model learned the *general rules* of performance.

2.  **Categorical Features:** We manually defined a list of low-cardinality features (like `reqCss`, `_renderBlockingJS`, `uses_cdn`).
    * **Why:** Telling LightGBM these are `category` types (not just numbers) allows it to find more complex, non-linear patterns (e.g., "1 CSS file is slow, 2-4 is fast, 5+ is slow again").

3.  **Output:** The script's output is a single `aislow_desktop.pkl` file.

## 4. The "Consultant" (`run_consultant.py`)

This is the final inference script that combines all our logic.

1.  **Explanation Engine:** We use `shap.TreeExplainer`.
2.  **SHAP's Needs (Key Insight):** The explainer needs *both* the `model.pkl` (the "brain") and the background `data.csv` (the "experience").
    * **Why:** The background data provides **context**. It's used to calculate the "average" page's score (`E[f(x)]`). All explanations are then calculated as "pushes" (red bars) or "pulls" (blue bars) away from that average.

3.  **Final Script Features:**
    * **Text Report:** It runs the analysis on a page (e.g., the median) and prints a human-readable text report.
    * **Friendly Names:** It uses a lookup table (`FEATURE_NAME_MAP`) to translate technical names (`_image_savings`) into friendly recommendations ("Potential Image Savings").
    * **"What-If" Analysis:** It automatically takes the **#1 problem** (e.g., `bytesTotal`) and runs a simulation to estimate the `SpeedIndex` savings from fixing it (e.g., "By cutting 'Total Page Size' in half, you could save **1079 ms**").
