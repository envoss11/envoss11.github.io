---
title: "Generative modelling in latent space"
source: "https://sander.ai/2025/04/15/latents.html"
site: "sander.ai"
date_read: 2025-04-18
raindrop_id: 1017391832
---

2 stages of training generative model:
1. train autoencoder (encoder + decoder - map input domain to 'latent' (condensed) representation)
2. train generative model on latent representation - autoregressive or diffusion

"However, it became clear very quickly that this strategy makes scaling up quite challenging. The most important reason for this can be summarised as follows: perceptual signals mostly consist of imperceptible noise. Or, to put it a different way: out of the total information content of a given signal, only a small fraction actually affects our perception of it. Therefore, it pays to ensure that our generative model can use its capacity efficiently, and focus on modelling just that fraction. That way, we can use smaller, faster and cheaper generative models without compromising on perceptual quality." 

Interesting note about the above - I suspect the "noise" isn't actually useless/meaningless, in the same way that saying a large portion of our genome is "junk" DNA is probably an oversimplification. Buffing out all the noise from the signal is probably what results in the kind of glossy, artificial tone that generative AI output (visual and textual) tends toward.

"What about language? This is not a perceptual modality, but maybe the two-stage approach could improve the efficiency of large language models as well? This is not straightforward, as it turns out. Language is inherently much less compressible than perceptual signals: it developed as a means of efficient communication, so there is considerably less redundancy. Which is not to say there isn’t any: Shannon famously estimated English to be 50% redundant99. But recall that images, audio and video can be compressed by several orders of magnitude with relatively minimal perceptual distortion, which is not possible with language without losing nuance or important semantic information."

"Tokenisers used for language models tend to be lossless (e.g. BPE95, SentencePiece93), so the resulting tokens aren’t usually viewed as “latents” "
