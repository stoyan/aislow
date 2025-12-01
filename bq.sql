WITH ParsedData AS (
  SELECT
    page,

    -- extracted & cast'd
    CAST(JSON_VALUE(summary, '$.SpeedIndex') AS INT64) AS SpeedIndex,
    CAST(JSON_VALUE(summary, '$.bytesTotal') AS INT64) AS totalBytes,
    
    -- Summary
    summary.TTFB,
    summary.renderStart,
    summary._connections AS numConnections,
    summary.numDomElements,
    summary.numDomains,
    summary.numRedirects,
    (JSON_VALUE(summary, '$.cdn') IS NOT NULL AND JSON_VALUE(summary, '$.cdn') != '') AS uses_cdn,

    -- Bytes & Request Counts
    summary.bytesCss,  summary.reqCss,
    summary.bytesJS,   summary.reqJS,
    summary.bytesImg,  summary.reqImg,
    summary.bytesFont, summary.reqFont,
    summary.bytesHtml, summary.reqHtml,
    summary.bytesJSON, summary.reqJSON,
    summary.reqTotal,
    summary.gzipSavings,

    -- Cache Control (MaxAge)
    summary.maxDomainReqs,
    summary.maxage0,
    summary.maxage1,
    summary.maxage30,
    summary.maxage365,
    summary.maxageMore,
    summary.maxageNull,

    -- Payload & CPU Metrics
    ARRAY_LENGTH(JSON_QUERY_ARRAY(payload, '$."_longTasks"')) AS num_long_tasks,
    payload._TotalBlockingTime as TotalBlockingTime,
    payload._cpuTimes.EvaluateScript,
    payload._cpuTimes.FunctionCall,
    payload._cpuTimes.Layout,
    payload._image_savings as image_savings,

    -- Render Blocking
    payload._renderBlockingCSS as renderBlockingCSS,
    payload._renderBlockingJS as renderBlockingJS,
    
    -- Paint Timing
    payload._firstContentfulPaint as FirstContentfulPaint,
    payload._firstImagePaint as FirstImagePaint,
    payload._firstMeaningfulPaint as FirstMeaningfulPaint,
    payload._firstPaint as FirstPaint,
    payload._chromeUserTiming.LargestContentfulPaint,

    -- count layout shifts
    (
      SELECT SUM(ARRAY_LENGTH(JSON_QUERY_ARRAY(shift, '$.rects')))
      FROM UNNEST(JSON_QUERY_ARRAY(payload, '$._LayoutShifts')) shift
    ) AS layout_shifts_count,

    -- Event durations
    (SAFE_CAST(JSON_VALUE(payload, '$._loadEventEnd') AS INT64) - 
     SAFE_CAST(JSON_VALUE(payload, '$._loadEventStart') AS INT64)) AS loadEventDuration,

    (SAFE_CAST(JSON_VALUE(payload, '$._domContentLoadedEventEnd') AS INT64) - 
     SAFE_CAST(JSON_VALUE(payload, '$._domContentLoadedEventStart') AS INT64)) AS dclDuration,

    -- Response Codes
    payload._responses_200,
    payload._responses_404,
    payload._responses_other,

    -- Technologies
    (SELECT COUNTIF('Analytics' IN UNNEST(categories)) FROM UNNEST(technologies)) AS analytics,
    (SELECT COUNTIF('Advertising' IN UNNEST(categories)) FROM UNNEST(technologies)) AS ads,
    (SELECT COUNTIF('Marketing automation' IN UNNEST(categories)) FROM UNNEST(technologies)) AS marketing,
    (SELECT COUNTIF('Font scripts' IN UNNEST(categories)) FROM UNNEST(technologies)) AS fonts_scripts,
    (SELECT COUNTIF('Tag managers' IN UNNEST(categories)) FROM UNNEST(technologies)) AS tagman,
    (SELECT COUNTIF('Live chat' IN UNNEST(categories)) FROM UNNEST(technologies)) AS chat,
    
    -- Custom metrics
    SAFE_CAST(JSON_VALUE(custom_metrics.markup, '$.images.img.dimensions.missing_width') AS INT64) AS img_missing_width,
    SAFE_CAST(JSON_VALUE(custom_metrics.markup, '$.images.img.dimensions.missing_height') AS INT64) AS img_missing_height,
    SAFE_CAST(JSON_VALUE(custom_metrics.markup, '$.images.img.loading.lazy') AS INT64) AS img_lazy_count,
    SAFE_CAST(JSON_VALUE(custom_metrics.markup, '$.svgs.svg_img_total') AS INT64) AS svg_count,
    custom_metrics.performance.is_lcp_preloaded,
    custom_metrics.javascript.script_tags.total as scripts_total,
    custom_metrics.javascript.script_tags.inline as scripts_inline,
    custom_metrics.javascript.script_tags.async as scripts_async,
    custom_metrics.javascript.script_tags.defer as scripts_defer,

  FROM
    `httparchive.crawl.pages`
  WHERE
    date = "2025-11-01"
    AND client = 'desktop'
    AND rank between 50000 and 100000
)

SELECT * FROM ParsedData
WHERE
  SpeedIndex BETWEEN 4500 AND 20000
  AND totalBytes > 10 * 1024
  AND numDomElements IS NOT NULL
ORDER BY RAND()
LIMIT 10000