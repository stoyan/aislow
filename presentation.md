# Electric Bike for the Brain

# Let's poke fun at AI

* Awfully performing V0-generated React
* https://fontes-locais.vercel.app/


# AI sucks!


# Stages of grief

denial, anger... acceptance


# Stages of AI grief

* Oh S@#$~, it will take my job (panic)
* Nah, never, it's not good enough (denial)
* Maybe it could one day take my job
* You know what, if it could, it should
* Please, take my job!

# AI is the best!

# About me

* Stoyan Stefanov
* Web performance enthusiast, since 2007?
* Yahoo, Facebook, WebPageTest, Etsy

# AI & web perf

* Research
* Investigate
* Test pages and scenarios
* Prototype
* Ship code to production

# Steve Jobs on computers

Bicycles for the mind


# AI is an electic bike for the mind

# Production code in my web perf day-to-day?


# MCP: Model Context Protocol 

# Chrome devtools


# MCP

"Open the browser, navigate to etsy.com, run a performance trace and give me top 3 areas for improvement"

# MCP

* It lies
* Keep asking questions

# Keep asing questions

* In general when interacting with AI tools
* AI happily generates new code
* It needs YOU to nudge towards good engineering practices
* Including performance

# Fixing the V0 code

# How about some DIY?


# Let's develop some AI


# ySlow

ySlow, PageSpeed, Lighthouse

# ySlow "rules"

# The Original 13

# aiSlow

Eh, I slow?

# Naïve take

Take a bunch of HARs and spit out wisdom!

# Easy there

* Raw messy JSON data is no good, Excel-like needed
* Target vs Features

# Crawl the web and collect!

* Nah, HTTPArchive instead
* Crawls million of pages monthly
* Data is in BigQuery


# Get some data

# Naïve take

Pick 10K random sites and learn!

# Easy there

* Data is all over the place
* Better: take a bunch of slow pages and and bunch of fast pages and learn

# Filter out pages

* too fast (error pages, forbidden, N/A in your country)
* too slow (temp issues, timeouts)


# Target & Features

* Target: SpeedIndex
* Features: 60-ish pieces of data



# Learning

**Regression** (predicting a number)
vs.
**Categorization** (cat/dog)

VS

**LLM**

VS 

Deep Learning


# LightGBM: Light Gradient Boosting Machine

A gradient boosting framework developed by Microsoft that uses tree-based learning algorithms

`LGBMRegressor` is a specific model class (vs Categorization)


# LightGBM

* Take structured CSV data with web performance metrics (bytes, requests, etc.)
* Train a regression model to predict SpeedIndex
* Use decision trees to find patterns in the data

#  ... as opposed to Deep Learning


# LightGBM (Gradient Boosting)

* Architecture: Ensemble of decision trees
* How it works: Builds trees sequentially, each correcting errors from previous trees
* Best for: Structured/tabular data (CSVs with rows and columns)
* Training: Fast (seconds to minutes)
* Interpretability: High - can see feature importance, SHAP values
* Data needs: Works well with small to medium datasets (thousands of rows)

# Deep Learning

* Architecture: Neural networks with multiple layers
* How it works: Layers of interconnected neurons that learn patterns
* Best for: Unstructured data (images, text, audio, video)
* Training: Slow (hours to days, needs GPUs)
* Interpretability: Low - "black box" behavior
* Data needs: Usually requires large datasets (millions of examples)


# Let's go!

# Input-magic-output

# Input

* Desktop-only
* Target: SpeedIndex
* Features: 60-ish pieces of data
* 20K+ fast pages (SI 500 - 2500ms)
* 20K+ slow pages (SI 4500 - 20000ms)

# Magic

* train_model.py
* 80/20 train/test split (test_size=0.2)
* Categorical Features
* DataFrame
* random_state=42     # reproducible results
* n_estimators=500    # Maximum number of boosting rounds
* learning_rate=0.05  # More careful, gradual learning
  * Prediction = Tree1 + 0.05 * Tree2 + 0.05 * Tree3 + ...
* stopping_rounds=10  # So we can exit before 500 rounds


# Output

* The Trained Model, aka The Brain
* `aislow_desktop.pkl`
* serialized model file, readable

# Understanding the output

* Training took 1.20 seconds.
* Best iteration: 111
* Model R-squared score on test data: 0.5754
* Feature importance

# Feature importance

* Gain >> Splits > Correlation
* Gain %: Best indicator of what the model actually relies on
* Splits: Shows usage frequency (but not impact)
* Correlation: Shows linear trends (but model sees more than just linear)


# Will it replicate ySlow's original 13?


# aiSlow

* "A web-perf consultant in a box"
* Given a page and the model, tell me what to improve
* Also needs the training data (or a representative sample)

# SHAP 

* SHapley Additive exPlanations
* Technnique for explaining machine learning model predictions
* Game theory: how much each player contributed in a game

# SHAP waterfalls

* Start with the average in the data set
* For each feature, calculate its impact, + or -

# aiSlow

* Show the top 3 + and top 3 - features
* 50ms+ only to reduce noise


# What-if scenario

* Take the top #1 worst offender
* Make its value be the 25 percentile
* Recalculate prediction

# Examples


# Will it take my job?


# Eyes on the price: faster web


# Plug

https://calendar.perfplanet.com


# Thank you!
