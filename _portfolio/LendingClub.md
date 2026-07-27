---
layout: project
order: 1
title: "Loan Marketing Segmentation"
excerpt: "An end-to-end project on public Lending Club data: build a classifier that tells a marketer which pitch to send, then ship it as a tool they can actually use."
image: /LoanMarketingHeader.png
image_fit: contain
tags_list:
  - "R"
  - "Shiny"
  - "caret"
  - "xgboost"
facts:
  - label: "Course"
    value: "STAT 656 — Applied Analytics"
  - label: "Data"
    value: "Public Lending Club loan listings"
  - label: "Deliverable"
    value: "Interactive R Shiny app"
links:
  - label: "Shiny app"
    icon: "external"
    url: "https://ericvoss.shinyapps.io/debtconsolidationapp/"
  - label: "GitHub repo"
    icon: "github"
    url: "https://github.com/envoss11/LendingClubProject"
  - label: "Full report"
    icon: "file"
    url: "/LCClean.html"
---

Using publicly available data from the crowd-sourced lending platform Lending Club, I set
out to build a classifier that would solve a marketing problem a company like this would
plausibly run into. One of the most popular loan types on the platform, debt consolidation,
is quite different from the rest from a marketing perspective. An ad for a debt
consolidation product speaks to the stress of juggling too many sources of debt, then
offers to simplify the situation. That is the exact opposite of the message you would send
to persuade someone to take on a *new* loan for a car or a home improvement project.

So I focused the analysis on a single question: is this prospective customer more likely to
want a debt consolidation product, or a more conventional loan?

## The deliverable

The final output was a Shiny app where a marketing employee enters what they know about a
prospect and gets back a recommendation — send the standard materials, or send the debt
consolidation pitch. I tried a range of models, including a classification tree along with
bagging and boosting methods, and settled on an xgboost-trained model that maximized
accuracy.

![Confusion Matrix](/confusionMatrix.png)
![ROC Curve](/ROC.png)

## How it did

The model does not produce mind-blowing results, but it is a clear improvement over
guessing which category a customer falls into. Playing with the app yields mostly sensible
behavior. Under the default parameters, a customer with 20 credit lines and 50% credit
utilization gets a debt consolidation recommendation. Drop that to 5 credit lines and 20%
utilization and the model stops suggesting debt consolidation.

![Default model parameters](/defaultparam.png)
![Adjusted model parameters](/newparam.png)

The full R Markdown report, with all the code and visualizations behind this, is linked at
the top of the page.
