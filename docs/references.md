# References

The idea is not new. The naming and the measurements come from the sources below. Context Keep is one way to apply them to the plain files you keep by hand.

- **Context engineering** is the discipline of curating what goes into the model's limited context window on each call. Anthropic, "Effective context engineering for AI agents": <https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents>

- **Context rot** is the measured degradation of output quality as input length grows. The phrase spread through community discussion and was measured across current models by Chroma's research. Chroma, "Context Rot: How Increasing Input Tokens Impacts LLM Performance": <https://www.trychroma.com/research/context-rot>

- **Lost in the middle** is the finding that long-context models use information at the start and end of the context better than the middle. Liu et al. (2023), "Lost in the Middle: How Language Models Use Long Contexts": <https://arxiv.org/abs/2307.03172>

Cost figures in this repository are illustrative. They use an input price you pass to the audit script and an estimated token count. For exact token counts, use your model's tokenizer or count_tokens endpoint.
