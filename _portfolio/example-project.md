---
title: "Loan Marketing Segmentation"
excerpt: "End-to-end project to build and deploy marketing model from Lending Club data"
header:
  image: /assets/images/foo-bar-identity.jpg
  teaser: /assets/images/foo-bar-identity-th.jpg
sidebar:
  - title: "Class"
    text: "STAT 656: Applied Analytics"
  - title: "Tools Used"
    text: "R, Shiny, Caret"
gallery:
  - url: /assets/images/unsplash-gallery-image-1.jpg
    image_path: assets/images/unsplash-gallery-image-1-th.jpg
    alt: "placeholder image 1"
  - url: /assets/images/unsplash-gallery-image-2.jpg
    image_path: assets/images/unsplash-gallery-image-2-th.jpg
    alt: "placeholder image 2"
  - url: /assets/images/unsplash-gallery-image-3.jpg
    image_path: assets/images/unsplash-gallery-image-3-th.jpg
    alt: "placeholder image 3"
---

Using publicly available data from crowd-sourced lending platform Lending Club, I set out to create a classifier which could predict what type of loan a customer might be interested in (auto loan, debt consolidation, etc.). Due to the large variety of loan types and the highly imbalanced nature of these categories, I settled on a somewhat more modest goal. 

Looking through the types of loans on the Lending Club platform, I realized that one of the most popular loan types, debt conslidation, was rather different than the rest from a marketing perspective. An advertisement for a debt consolidation product would likely relate to the stress caused by having too many sources of debt, and then offer to help them simplify that situation. This is the exact opposite of the message one would want to send to persuade a customer to take on a new loan for something like a car or home improvements. As a result, I chose to focus my analysis on predicting whether a client would be more likely interested in debt consolidation products or other, more conventional loans. 

{% include gallery caption="This is a sample gallery to go along with this case study." %}