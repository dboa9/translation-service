---
license: gemma
library_name: transformers
pipeline_tag: text-generation
extra_gated_button_content: Acknowledge license
tags:
- conversational
language:
- ar
- ary
datasets:
- MBZUAI-Paris/Darija-SFT-Mixture
base_model:
- google/gemma-2-9b-it
---


# JAIS Intiative: Atlas-Chat Models


## Model Overview

Atlas-Chat is a family of open models instruction-tuned for Darija, the colloquial Arabic of Morocco, developed as part of the [Jais](https://arxiv.org/abs/2308.16149) project for standard Arabic and its extentions to dialectal Arabic. These models are designed for language generation and excel in various applications such as question answering, summarization, and translation. Thanks to their compact size, Atlas-Chat models can be deployed in resource-constrained environments like laptops, desktops, or personal cloud setups, making advanced AI accessible to Darija speakers and promoting widespread innovation. Three sizes are available:
* [Atlas-Chat-2B](https://huggingface.co/MBZUAI-Paris/Atlas-Chat-2B): A small-sized version with 2 billion parameters, capable of generating fluent Moroccan Darija text while maintaining efficiency.
* [Atlas-Chat-9B](https://huggingface.co/MBZUAI-Paris/Atlas-Chat-9B): A medium-sized with 9 billion parameters, providing more nuanced, contextually rich language generation for complex tasks.
* [Atlas-Chat-27B](https://huggingface.co/MBZUAI-Paris/Atlas-Chat-27B): A large-sized version with 27 billion parameters, offering even more advanced capabilities for complex tasks and nuanced language generation compared to the 2B and 9B versions.

The models are designed to assist with:

* Conversational agents and chatbots that operate in Darija.
* Translation, summarization, and content generation in informal dialect.
* Cultural research related to Morocco and its language.

**Paper:** [Atlas-Chat: Adapting Large Language Models for Low-Resource Moroccan Arabic Dialect](https://arxiv.org/abs/2409.17912)

## 👥 Our Team

The model is developed by MBZUAI France Lab, an AI research center in Paris affiliated with the [Mohamed bin Zayed University of Artificial Intelligence (MBZUAI)](https://mbzuai.ac.ae/) headquartered in Abu Dhabi.


## Usage

Below we share some code snippets on how to get quickly started with running the model. First, install the Transformers library with:

```sh
pip install -U transformers sentencepiece
```

Then, copy the snippet from the section that is relevant for your use case.

#### Running with the `pipeline` API

```python
import torch
from transformers import pipeline

pipe = pipeline(
    "text-generation",
    model="MBZUAI-Paris/Atlas-Chat-9B",
    model_kwargs={"torch_dtype": torch.bfloat16},
    device="cuda" # replace with "mps" to run on a Mac device
)

messages = [
    {"role": "user", "content": 'شكون لي صنعك؟'},
]

outputs = pipe(messages, max_new_tokens=256, temperature=0.0)
assistant_response = outputs[0]["generated_text"][-1]["content"].strip()
print(assistant_response)
```

- Response:


>صنعاتني جامعة محمد بن زايد للذكاء الاصطناعي، لي هي جامعة بحثية ديال الدراسات العليا الهدف ديالها أنها تزيد بالذكاء الاصطناعي لقدّام وتنفع بيه الإنسانية. يمكن ليك تزور https://mbzuai.ac.ae/ar/about/ باش تعرف كثر على جامعة محمد بن زايد للذكاء الاصطناعي والمهمة ديالها!


#### Running the model on a single / multi GPU

```sh
pip install accelerate
```

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model_id = "MBZUAI-Paris/Atlas-Chat-9B"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="auto",
    torch_dtype=torch.bfloat16,
)

messages = [
    {"role": "user", "content": "شنو كيتسمى المنتخب المغربي ؟"},
]

input_ids = tokenizer.apply_chat_template(messages, return_tensors="pt", return_dict=True, , add_generation_prompt=True)

outputs = model.generate(**input_ids, max_new_tokens=256)

print(tokenizer.decode(outputs[0]))
```

- Response:
>المنتخب المغربي كيتسمى أيضا "أسود الأطلس"


<!-- You can ensure the correct chat template is applied by using `tokenizer.apply_chat_template` as follows:
```python

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model_id = "MBZUAI-Paris/Atlas-Chat-9B"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="auto",
    torch_dtype=torch.bfloat16,
)

messages = [
    {"role": "user", "content": "شنو هيا الإيجابيات ديال الطاقة المتجددة؟"},
]
input_ids = tokenizer.apply_chat_template(messages, return_tensors="pt", return_dict=True, add_generation_prompt=True)

outputs = model.generate(**input_ids, max_new_tokens=256, temperature=0.0)

print(tokenizer.decode(outputs[0]))
```

- Response:
```text
<bos><start_of_turn>user
شنو هيا الإيجابيات ديال الطاقة المتجددة؟<end_of_turn>
<start_of_turn>model
الطاقة المتجددة عندها بزاف ديال الإيجابيات، منها:

1. الاستدامة: مصادر الطاقة المتجددة بحال الريح، الشمس، والطاقة الكهرومائية كيتجددو بشكل طبيعي، يعني ما غاديش ينفدو مع الوقت. هاد الشي كيخليهم مصدر طاقة مستدام اللي ممكن نعتمدو عليه على المدى الطويل.

2. تقليل انبعاثات الكربون: مصادر الطاقة المتجددة عموماً عندها انبعاثات كربونية أقل من الوقود الأحفوري، وهاد الشي كيساعد فالتخفيف من التغير المناخي وتقليل تلوث الهواء.

3. الاستقلال الطاقي: مصادر الطاقة المتجددة ممكن نستعملوها باش نقللو من الاعتماد على الوقود الأحفوري المستورد، وهاد الشي كيزيد من الاستقلال الطاقي وكيقلل من خطر التقطيع.

4. خلق فرص الشغل: صناعة الطاقة المتجددة كتخلق فرص شغل فمجالات بحال تركيب الألواح الشمسية، صيانة توربينات الرياح، وبناء محطات
``` -->

#### Quantized Versions through `bitsandbytes`

<details>
  <summary>
    Using 8-bit precision (int8)  
  </summary>

```sh
pip install bitsandbytes accelerate
```

```python
# pip install bitsandbytes accelerate
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

model_id = "MBZUAI-Paris/Atlas-Chat-9B"
quantization_config = BitsAndBytesConfig(load_in_8bit=True)

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    quantization_config=quantization_config,
)
text = f"""
        شرح ليا هاد الهضرة:
        في القرن 19 لقاو الذّهب في كاليفورنيا، ناضو لّي كيبيعو العتلة والفاس كيقنعو الناس بلي غيديرو لاباس يلا قلبو على الذهب... فالأخير اغتنى تجار أدوات التنقيب والحفر. وحاليا كاين لّي كيقنع الأخرين بلي هو مليونير، وعندو الوقت يورّي للآخرين كيفاش يديرو لاباس.
        """
messages = [
    {"role": "user", "content": text},
]
input_ids = tokenizer.apply_chat_template(messages, return_tensors="pt", return_dict=True).to("cuda")

outputs = model.generate(**input_ids, max_new_tokens=256)
print(tokenizer.decode(outputs[0]).split("<start_of_turn>model")[-1])
```

- Response:

>هاد الهضرة كتهضر على قصة قديمة من القرن 19 فين تكتشف الذهب فكاليفورنيا. هاد الشي خلق حالة ديال الجنون على الذهب، فين بزاف ديال الناس مشاو لتما باش يقلبو عليه. كانو حتى ناس اللي كانو كيبيعو أدوات التنقيب بحال الفاس والعتلة، وكانو كيقنعو الناس بلي غادي يربحو الفلوس إلا مشاو يقلبو على الذهب. فالنهاية، هادوك اللي كانو كيبيعو هاد الأدوات هوما اللي ربحو بزاف، حيت كانو كيربحو من كل واحد اللي كان كيشري منهم.
>
>هاد القصة كتشبه للي كاينة دابا، فين كاينين ناس اللي كيدعيو بلي هوما مليونير وكيبيعو نصائح على كيفاش تربح الفلوس. بحال هادوك اللي كانو كيبيعو الأدوات فالماضي، حتى هاد الناس كيربحو من هاد الشي، حيت كياخدو الفلوس من الناس اللي كيشريو منهم النصائح ديالهم.


</details>

<details>
  <summary>
    Using 4-bit precision  
  </summary>

```python
# pip install bitsandbytes accelerate
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

model_id = "MBZUAI-Paris/Atlas-Chat-9B"
quantization_config = BitsAndBytesConfig(load_in_4bit=True)

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    quantization_config=quantization_config,
)
text = f"""ترجم للدارجة:
Atlas Chat is the first open source large language model that talks in Darija.
        """
messages = [
    {"role": "user", "content": text},
]
input_ids = tokenizer.apply_chat_template(messages, return_tensors="pt", return_dict=True, add_generation_prompt=True)

outputs = model.generate(**input_ids, max_new_tokens=256, temperature=0.0)
print(tokenizer.decode(outputs[0]).split("<start_of_turn>model")[-1])
```

- Response:

>أطلّاس شات هو أول نموذج لغوي كبير مفتوح المصدر كايهضر بالدارجة.


</details>


### Chat Template

The models use a chat template that must be adhered to conversational use.
The easiest way to apply it is using the tokenizer's built-in chat template, as shown in the following snippet.

Let's load the model and apply the chat template to a conversation. In this example, we'll start with a single user interaction:

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
import transformers
import torch

model_id = "MBZUAI-Paris/Atlas-Chat-9B"
dtype = torch.bfloat16

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="cuda",
    torch_dtype=dtype,)

chat = [
    { "role": "user", "content": "أشنو كايمييز المملكة المغربية." },
]
prompt = tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
```

At this point, the prompt contains the following text:

```
<bos><start_of_turn>user
أشنو كايمييز المملكة المغربية.<end_of_turn>
<start_of_turn>model
```

As you can see, each turn is preceded by a `<start_of_turn>` delimiter and then the role of the entity
(either `user`, for content supplied by the user, or `model` for LLM responses). Turns finish with
the `<end_of_turn>` token.

You can follow this format to build the prompt manually, if you need to do it without the tokenizer's
chat template.

After the prompt is ready, generation can be performed like this:

```python
inputs = tokenizer.encode(prompt, add_special_tokens=False, return_tensors="pt")
outputs = model.generate(input_ids=inputs.to(model.device), max_new_tokens=512)
print(tokenizer.decode(outputs[0]))
```

- Response:

>المغرب كايميزو بزاف ديال الحوايج، منهم:
>
>1. التنوع الثقافي: المغرب بلاد فيها بزاف ديال الثقافات، كل وحدة فيهم عندها التقاليد ديالها واللغة ديالها والماكلة ديالها. هاد التنوع كايبان فالموسيقى والرقص والفنون التقليدية.
>
>2. التراث التاريخي: المغرب عندو تاريخ غني كايمتد لآلاف السنين، فيه حضارات قديمة بحال مملكة موريطانيا، والرومان، والبيزنطيين، والفتوحات الإسلامية. هاد التراث كايبان فالمعالم التاريخية بحال مدينة فاس، والمدينة القديمة ديال مراكش، والمدينة القديمة ديال شفشاون.
>
>3. المناظر الطبيعية: المغرب بلاد فيها مناظر طبيعية متنوعة، من السواحل الزرقة والصحاري الكبيرة، للجبال العالية والوديان الخضراء. هاد التنوع كايمكنك من ممارسة أنشطة خارجية بحال المشي لمسافات طويلة، والتخييم، والرياضات المائية.
>
>4. الماكلة: الماكلة المغربية معروفة بالتنوع ديالها والطعم ديالها. من بين الأطباق الأكثر شعبية كاين الطاجين، والكسكس، والبريوات، والكوكتيل ديال الفواكه.
>
>5. الناس: المغاربة معروفين بالضيافة ديالهم والترحاب ديالهم. كايكونو فرحانين باش يشاركو الثقافة والتقاليد ديالهم مع الزوار.




### Inputs and outputs

*   **Input:** Text string, such as a question, a prompt, or a document to be
    summarized.
*   **Output:** Generated Darija text in response to the input, such
    as an answer to a question, or a summary of a document.

### Chatbot interface using Ollama

You can also use Ollama and chatbot-ollama to create a chatbot user-interface to better test the model.
First you need to install Ollama on your machine from [here](https://github.com/ollama/ollama) and have node.js installed as well. Then, download and prepare the model as follows:
```bash

huggingface-cli download MBZUAI-Paris/Atlas-Chat-9B --local-dir Atlas-Chat-9B/
ollama create Atlas-Chat-9B -f Atlas-Chat-9B/modelfile
ollama serve
```
Finally, in a new terminal clone chatbot-ollama repository from Github and run it:
```bash
git clone https://github.com/ivanfioravanti/chatbot-ollama.git
cd chatbot-ollama
npm ci
npm run dev
```
You can start chatting with the model by visiting http://localhost:3000.
### Citation
If you use Atlas-Chat in your research, please cite our paper:
```none
@article{shang2024atlaschatadaptinglargelanguage,
      title={Atlas-Chat: Adapting Large Language Models for Low-Resource Moroccan Arabic Dialect}, 
      author={Guokan Shang and Hadi Abdine and Yousef Khoubrane and Amr Mohamed and Yassine Abbahaddou and Sofiane Ennadir and Imane Momayiz and Xuguang Ren and Eric Moulines and Preslav Nakov and Michalis Vazirgiannis and Eric Xing},
      year={2024},
      eprint={2409.17912},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2409.17912}, 
}
```




## Training Data
The model was trained on diverse datasets focusing on Darija consisting for approximatley 450k instructions of a maximum length of 2048 tokens, including:

* Synthetic instructions created to guide the model in processing various types of language tasks tailord towards Moroccan culture.
* Instruction samples created from publicly available Moroccan Arabic datasets including translation, summarization and sentiment analysis.
* Translated English and multi-lingual instruction-tuning datasets.

Our training dataset [Darija-SFT-Mixture](https://huggingface.co/datasets/MBZUAI-Paris/Darija-SFT-Mixture) is publicly available.


## Implementation Information
Atlas-Chat models are based on Gemma 2 models. The Atlas-Chat models were trained using 8 Nvidia's A100 80 GB GPUs in parallel using FSDP on AWS Sagemaker. The model is trained using HuggingFace transformers and parameter-efficient fine-tuning with LoRA rank of 256.


## Evaluation
The Atlas-Chat models were evaluated on a comprehensive suite of tasks using various datasets and benchmarks to assess their performance across multiple dimensions. These included tasks such as:

* **DarijaMMLU:** A Darija version of ArabicMMLU and MMLU benchmarks translated from MSA and English respectively.
* **DarijaHellaSwag:** A Darija version of HellaSwag.
* **Belebele Ary_Arab:** Belebele is a multiple-choice machine reading comprehension dataset published by Facebook spanning 122 language variants. The Evaluation is done on the Ary_Arab part of Belebele that refers to Darija.
* **DarijaAlpacaEval:** A Darija version of AlpacaEval translated to Darija and adapted to the Moroccan culture.
* **Sentiment Analysis.**
* **Translation:** Including six directions and four languages: Darija, MSA, English and French.
* **Transliteration:** Transforming a sentence from Darija (written in Arabic characters) to Arabizi (Written in Latin characters) and vice-versa.
* **Summarization.**

The models were compared against a collection of existing open-source Arabic models to gauge their effectiveness, with a particular focus on performance in Darija. All scores are based on zero-shot performance. The prompts are written mainly in Darija. The metric used for DarijaMMLU, DarijaHellaSwag, Belebele Ary and Sentiment Analysis is the normalized accuracy. We used [Language Model Evaluation Harness](https://github.com/MBZUAI-Paris/lm-evaluation-harness-atlas-chat) to conduct these evaluations.

**LLMs Benchmarks:**
<table>
    <tr>
        <td>Model</td>
        <td><a href="https://huggingface.co/datasets/MBZUAI-Paris/DarijaMMLU" target="_blank">DarijaMMLU</a></td>
        <td><a href="MBZUAI-Paris/DarijaHellaSwag" target="_blank">DarijaHellaSwag</a></td>
        <td ><a href="https://huggingface.co/datasets/facebook/belebele/viewer/ary_Arab" target="_blank">Belebele Ary</a></td>
        <td ><a href="https://huggingface.co/datasets/MBZUAI-Paris/DarijaAlpacaEval" target="_blank">DarijaAlpacaEval</a></td>
    </tr>
    <tr>
        <td><a href="https://huggingface.co/inceptionai/jais-family-1p3b-chat" target="_blank">jais-family-1p3b-chat</a></td>
        <td>35.39</td>
        <td>27.71</td>
        <td>38.33</td>
        <td>35.56</td>
    </tr>
    <tr>
        <td><a href="https://huggingface.co/inceptionai/jais-family-2p7b-chat" target="_blank">jais-family-2p7b-chat</a></td>
        <td>37.44</td>
        <td>29.10</td>
        <td>44.11</td>
        <td>52.97</td>
    </tr>
    <tr>
        <td><a href="https://huggingface.co/google/gemma-2-2b-it" target="_blank">gemma-2-2b-it</a></td>
        <td>28.58</td>
        <td>32.42</td>
        <td>25.22</td>
        <td>58.67</td>
    </tr>
    <tr>
        <td><a href="meta-llama/Llama-3.2-1B-Instruct" target="_blank">Llama-3.2-1B-Instruct</a></td>
        <td>27.66</td>
        <td>26.88</td>
        <td>28.89</td>
        <td>23.57</td>
    </tr>
    <tr>
        <td><a href="meta-llama/Llama-3.2-3B-Instruct" target="_blank">Llama-3.2-3B-Instruct</a></td>
        <td>32.60</td>
        <td>28.33</td>
        <td>38.00</td>
        <td>47.62</td>
    </tr>
    <tr>
        <td><strong><a href="https://huggingface.co/MBZUAI-Paris/Atlas-Chat-2B" target="_blank">Atlas-Chat-2B</a></strong></td>
        <td><b>44.97</b></td>
        <td><b>35.08</b></td>
        <td><b>53.89</b></td>
        <td><b>92.31</b></td>
    </tr>
    <tr style="border-top: 4px solid;"></tr>
    <tr>
        <td><a href="https://huggingface.co/inceptionai/jais-family-6p7b-chat" target="_blank">jais-family-6p7b-chat</a></td>
        <td>39.96</td>
        <td>32.64</td>
        <td>51.22</td>
        <td>65.18</td>
    </tr>
    <tr>
        <td><a href="https://huggingface.co/inceptionai/jais-adapted-7b-chat" target="_blank">jais-adapted-7b-chat</a></td>
        <td>39.30</td>
        <td>29.55</td>
        <td>43.67</td>
        <td>61.84</td>
    </tr>
    <tr>
        <td><a href="https://huggingface.co/inceptionai/jais-family-13b-chat" target="_blank">jais-family-13b-chat</a></td>
        <td>45.11</td>
        <td>33.98</td>
        <td>58.67</td>
        <td>69.93</td>
    </tr>
    <tr>
        <td><a href="https://huggingface.co/inceptionai/jais-adapted-13b-chat" target="_blank">jais-adapted-13b-chat</a></td>
        <td>45.20</td>
        <td>32.84</td>
        <td>49.67</td>
        <td>77.52</td>
    </tr>
    <tr>
        <td><a href="https://huggingface.co/FreedomIntelligence/AceGPT-7B-chat" target="_blank">AceGPT-7b-chat</a></td>
        <td>35.98</td>
        <td>30.33</td>
        <td>30.11</td>
        <td>47.31</td>
    </tr>
    <tr>
        <td><a href="https://huggingface.co/FreedomIntelligence/AceGPT-13B-chat" target="_blank">AceGPT-13b-chat</a></td>
        <td>41.09</td>
        <td>38.35</td>
        <td>33.11</td>
        <td>52.79</td>
    </tr>
    <tr>
        <td><a href="https://huggingface.co/google/gemma-2-9b-it" target="_blank">gemma-2-9b-it</a></td>
        <td>35.91</td>
        <td>32.19</td>
        <td>31.00</td>
        <td>90.86</td>
    </tr>
    <tr>
        <td><a href="meta-llama/Meta-Llama-3.1-8B-Instruct" target="_blank">Llama-3.1-8B-Instruct</a></td>
        <td>44.13</td>
        <td>31.40</td>
        <td>47.00</td>
        <td>78.08</td>
    </tr>
    <tr>
        <td><strong><a href="https://huggingface.co/MBZUAI-Paris/Atlas-Chat-9B" target="_blank">Atlas-Chat-9B</a></strong></td>
        <td><b>58.23</b></td>
        <td><b>43.65</b></td>
        <td><b>74.56</b></td>
        <td><b>95.62</b></td>
    </tr>
    <tr style="border-top: 4px solid;"></tr>
    <tr>
        <td><a href="https://huggingface.co/inceptionai/jais-family-30b-8k-chat" target="_blank">jais-family-30b-8k-chat</a></td>
        <td>51.88</td>
        <td>35.61</td>
        <td>65.67</td>
        <td>24.64</td>
    </tr>
    <tr>
        <td><a href="https://huggingface.co/google/gemma-2-27b-it" target="_blank">gemma-2-27b-it</a></td>
        <td>36.47</td>
        <td>37.04</td>
        <td>35.78</td>
        <td>95.07</td>
    </tr>
    <tr>
        <td><strong><a href="https://huggingface.co/MBZUAI-Paris/Atlas-Chat-27B" target="_blank">Atlas-Chat-27B</a></strong></td>
        <td><b>61.95</b></td>
        <td><b>48.37</b></td>
        <td><b>75.67</b></td>
        <td><b>96.58</b></td>
    </tr>
</table>

**Standard NLP Tasks:**
<table>
    <tr>
        <td rowspan="2">Model</td>
        <td colspan="2"><a href="https://huggingface.co/datasets/MBZUAI-Paris/DarijaBench" target="_blank">DODa-10k (Translation)</a></td>
        <td colspan="2"><a href="https://huggingface.co/datasets/MBZUAI-Paris/DarijaBench" target="_blank">MADAR (Translation)</a></td>
        <td colspan="2"><a href="https://huggingface.co/datasets/MBZUAI-Paris/DarijaBench" target="_blank">FLORES+ (Translation)</a></td>
        <td colspan="2"><a href="https://huggingface.co/datasets/MBZUAI-Paris/DarijaBench" target="_blank">NLLB-Seed (Translation)</a></td>
        <td colspan="2"><a href="https://huggingface.co/datasets/MBZUAI-Paris/DarijaBench" target="_blank">DODa-10k (Transliteration)</a></td>
        <td rowspan="2"><a href="https://huggingface.co/datasets/MBZUAI-Paris/DarijaBench" target="_blank">MArSum (Summarization)</a><br/>(LLM as a judge)</td>
        <td rowspan="2"><a href="https://huggingface.co/datasets/MBZUAI-Paris/DarijaBench" target="_blank">Sentiment Analysis</a></td>
    </tr>
    <tr>
        <td>BLEU</td>
        <td>chrF</td>
        <td>BLEU</td>
        <td>chrF</td>
        <td>BLEU</td>
        <td>chrF</td>
        <td>BLEU</td>
        <td>chrF</td>
        <td>BLEU</td>
        <td>chrF</td>
    </tr>
    <tr>
        <td><a href="https://huggingface.co/inceptionai/jais-family-1p3b-chat" target="_blank">jais-family-1p3b-chat</a></td>
        <td>00.13</td>
        <td>06.18</td>
        <td>00.50</td>
        <td>15.43</td>
        <td>02.44</td>
        <td>19.14</td>
        <td>01.99</td>
        <td>12.60</td>
        <td>00.01</td>
        <td>03.01</td>
        <td>00.50</td>
        <td>45.29</td>
    </tr>
    <tr>
        <td><a href="https://huggingface.co/inceptionai/jais-family-2p7b-chat" target="_blank">jais-family-2p7b-chat</a></td>
        <td>00.25</td>
        <td>07.46</td>
        <td>00.62</td>
        <td>16.36</td>
        <td>04.25</td>
        <td>18.22</td>
        <td>03.10</td>
        <td>08.19</td>
        <td>00.01</td>
        <td>03.27</td>
        <td>00.90</td>
        <td>51.56</td>
    </tr>
    <tr>
        <td><a href="https://huggingface.co/google/gemma-2-2b-it" target="_blank">gemma-2-2b-it</a></td>
        <td>00.10</td>
        <td>04.96</td>
        <td>00.12</td>
        <td>06.66</td>
        <td>01.55</td>
        <td>18.59</td>
        <td>02.78</td>
        <td>23.69</td>
        <td>00.01</td>
        <td>02.08</td>
        <td>06.80</td>
        <td>53.36</td>
    </tr>
    <tr>
        <td><a href="meta-llama/Llama-3.2-1B-Instruct" target="_blank">Llama-3.2-1B-Instruct</a></td>
        <td>00.07</td>
        <td>05.95</td>
        <td>00.80</td>
        <td>18.71</td>
        <td>04.53</td>
        <td>18.39</td>
        <td>04.52</td>
        <td>17.06</td>
        <td>00.02</td>
        <td>03.74</td>
        <td>08.23</td>
        <td>46.27</td>
    </tr>
    <tr>
        <td><a href="meta-llama/Llama-3.2-3B-Instruct" target="_blank">Llama-3.2-3B-Instruct</a></td>
        <td>00.62</td>
        <td>13.67</td>
        <td>01.18</td>
        <td>22.12</td>
        <td>08.59</td>
        <td>35.21</td>
        <td>13.75</td>
        <td>43.63</td>
        <td>00.21</td>
        <td>09.68</td>
        <td>08.23</td>
        <td>49.20</td>
    </tr>
    <tr>
        <td><strong><a href="https://huggingface.co/MBZUAI-Paris/Atlas-Chat-2B" target="_blank">Atlas-Chat-2B</a></strong></td>
        <td><b>22.76</td>
        <td><b>44.86</td>
        <td><b>16.67</td>
        <td><b>41.64</td>
        <td><b>14.92</td>
        <td><b>43.03</td>
        <td><b>23.88</td>
        <td><b>52.19</td>
        <td><b>08.18</td>
        <td><b>21.54</td>
        <td><b>55.22</td>
        <td><b>73.99</td>
    </tr>
    <tr style="border-top: 4px solid;"></tr>
    <tr>
        <td><a href="https://huggingface.co/inceptionai/jais-family-6p7b-chat" target="_blank">jais-family-6p7b-chat</a></td>
        <td>00.73</td>
        <td>11.85</td>
        <td>01.88</td>
        <td>23.22</td>
        <td>04.25</td>
        <td>18.22</td>
        <td>04.62</td>
        <td>20.22</td>
        <td>00.02</td>
        <td>03.79</td>
        <td>03.02</td>
        <td>56.78</td>
    </tr>
    <tr>
        <td><a href="https://huggingface.co/inceptionai/jais-adapted-7b-chat" target="_blank">jais-adapted-7b-chat</a></td>
        <td>00.60</td>
        <td>09.43</td>
        <td>03.45</td>
        <td>25.88</td>
        <td>07.25</td>
        <td>23.21</td>
        <td>01.25</td>
        <td>02.22</td>
        <td>00.04</td>
        <td>03.24</td>
        <td>02.82</td>
        <td>52.72</td>
    </tr>
    <tr>
        <td><a href="https://huggingface.co/inceptionai/jais-family-13b-chat" target="_blank">jais-family-13b-chat</a></td>
        <td>00.92</td>
        <td>11.71</td>
        <td>04.01</td>
        <td>28.48</td>
        <td>05.70</td>
        <td>27.24</td>
        <td>04.50</td>
        <td>22.56</td>
        <td>00.03</td>
        <td>03.57</td>
        <td>01.77</td>
        <td>41.73</td>
    </tr>
    <tr>
        <td><a href="https://huggingface.co/inceptionai/jais-adapted-13b-chat" target="_blank">jais-adapted-13b-chat</a></td>
        <td>00.87</td>
        <td>10.52</td>
        <td>04.02</td>
        <td>25.29</td>
        <td>06.66</td>
        <td>23.46</td>
        <td>20.14</td>
        <td>47.87</td>
        <td>0.04</td>
        <td>04.77</td>
        <td>01.92</td>
        <td>66.68</td>
    </tr>
    <tr>
        <td><a href="https://huggingface.co/FreedomIntelligence/AceGPT-7B-chat" target="_blank">AceGPT-7b-chat</a></td>
        <td>00.44</td>
        <td>11.33</td>
        <td>01.05</td>
        <td>19.24</td>
        <td>06.92</td>
        <td>36.03</td>
        <td>11.05</td>
        <td>44.55</td>
        <td>00.06</td>
        <td>04.74</td>
        <td>02.28</td>
        <td>40.23</td>
    </tr> 
    <tr>
        <td><a href="https://huggingface.co/FreedomIntelligence/AceGPT-13B-chat" target="_blank">AceGPT-13b-chat</a></td>
        <td>00.98</td>
        <td>16.70</td>
        <td>00.81</td>
        <td>20.23</td>
        <td>08.73</td>
        <td>40.76</td>
        <td>14.02</td>
        <td>48.28</td>
        <td>00.12</td>
        <td>06.32</td>
        <td>02.80</td>
        <td>59.58</td>
    </tr>
    <tr>
        <td><a href="https://huggingface.co/google/gemma-2-9b-it" target="_blank">gemma-2-9b-it</a></td>
        <td>03.10</td>
        <td>19.16</td>
        <td>01.72</td>
        <td>24.35</td>
        <td>05.18</td>
        <td>36.96</td>
        <td>08.23</td>
        <td>43.57</td>
        <td>00.17</td>
        <td>09.14</td>
        <td>13.81</td>
            <td>59.87</td>
    </tr>
    <tr>
        <td><a href="meta-llama/Meta-Llama-3.1-8B-Instruct" target="_blank">Llama-3.1-8B-Instruct</a></td>
        <td>00.92</td>
        <td>14.19</td>
        <td>01.46</td>
        <td>23.82</td>
        <td>08.89</td>
        <td>33.08</td>
        <td>11.85</td>
        <td>35.51</td>
        <td>00.11</td>
        <td>06.02</td>
        <td>16.14</td>
        <td>44.08</td>
    </tr>
    <tr>
        <td><strong><a href="https://huggingface.co/MBZUAI-Paris/Atlas-Chat-9B" target="_blank">Atlas-Chat-9B</a></strong></td>
        <td><b>28.08</td>
        <td><b>50.48</td>
        <td><b>18.16</td>
        <td><b>43.91</td>
        <td><b>18.63</td>
        <td><b>47.53</td>
        <td><b>29.98</td>
        <td><b>58.26</td>
        <td><b>22.08</td>
        <td><b>34.17</td>
        <td><b>59.76</td>
        <td><b>81.89</td>
    </tr>
    <tr style="border-top: 4px solid;"></tr>
    <tr>
        <td><a href="https://huggingface.co/inceptionai/jais-family-30b-8k-chat" target="_blank">jais-family-30b-8k-chat</a></td>
        <td>01.10</td>
        <td>14.40</td>
        <td>01.67</td>
        <td>23.37</td>
        <td>08.52</td>
        <td>35.41</td>
        <td>13.71</td>
        <td>41.33</td>
        <td>00.05</td>
        <td>04.48</td>
        <td>00.46</td>
        <td>56.73</td>
    </tr>
    <tr>
        <td><a href="https://huggingface.co/google/gemma-2-27b-it" target="_blank">gemma-2-27b-it</a></td>
        <td>00.67</td>
        <td>13.04</td>
        <td>01.74</td>
        <td>24.63</td>
        <td>05.17</td>
        <td>37.08</td>
        <td>07.36</td>
        <td>42.49</td>
        <td>00.03</td>
        <td>04.94</td>
        <td>11.10</td>
        <td>57.59</td>
    </tr>
    <tr>
        <td><strong><a href="https://huggingface.co/MBZUAI-Paris/Atlas-Chat-27B" target="_blank">Atlas-Chat-27B</a></strong></td>
        <td><b>29.55</td>
        <td><b>51.74</td>
        <td><b>19.66</td>
        <td><b>45.65</td>
        <td><b>20.34</td>
        <td><b>49.19</td>
        <td><b>31.61</td>
        <td><b>59.37</td>
        <td><b>33.03</td>
        <td><b>40.95</td>
        <td><b>60.70</td>
        <td>73.00</td>
    </tr>


    
</table>

## Usage and Limitations

These models have certain limitations that users should be aware of.
<details>
<summary>Intended Usage</summary>

Open Large Language Models (LLMs) have a wide range of applications across
various industries and domains. The following list of potential uses is not
comprehensive. The purpose of this list is to provide contextual information
about the possible use-cases that the model creators considered as part of model
training and development.

* Content Creation and Communication
  * Text Generation: These models can be used to generate creative text formats
    such as poems, scripts, code, marketing copy, and email drafts.
  * Chatbots and Conversational AI: Power conversational interfaces for customer
    service, virtual assistants, or interactive applications.
  * Text Summarization: Generate concise summaries of a text corpus, research
    papers, or reports.
* Research and Education
  * Natural Language Processing (NLP) Research: These models can serve as a
    foundation for researchers to experiment with NLP techniques, develop
    algorithms, and contribute to the advancement of the field.
  * Language Learning Tools: Support interactive language learning experiences,
    aiding in grammar correction or providing writing practice.
  * Knowledge Exploration: Assist researchers in exploring large bodies of text
    by generating summaries or answering questions about specific topics.
</details>
<details>
<summary>Limitations</summary>

* Training Data
  * The quality and diversity of the training data significantly influence the
    model's capabilities. Biases or gaps in the training data can lead to
    limitations in the model's responses.
  * The scope of the training dataset determines the subject areas the model can
    handle effectively.
* Context and Task Complexity
  * LLMs are better at tasks that can be framed with clear prompts and
    instructions. Open-ended or highly complex tasks might be challenging.
  * A model's performance can be influenced by the amount of context provided
    (longer context generally leads to better outputs, up to a certain point).
* Language Ambiguity and Nuance
  * Natural language is inherently complex. LLMs might struggle to grasp subtle
    nuances, sarcasm, or figurative language.
* Factual Accuracy
  * LLMs generate responses based on information they learned from their
    training datasets, but they are not knowledge bases. They may generate
    incorrect or outdated factual statements.
* Common Sense
  * LLMs rely on statistical patterns in language. They might lack the ability
    to apply common sense reasoning in certain situations.
</details>
<details>
<summary> Ethical Considerations and Risks</summary>

The development of large language models (LLMs) raises several ethical concerns.
In creating an open model, we have carefully considered the following:

* Bias and Fairness
  * LLMs trained on large-scale, real-world text data can reflect socio-cultural
    biases embedded in the training material.
* Misinformation and Misuse
  * LLMs can be misused to generate text that is false, misleading, or harmful.
  * Guidelines are provided for responsible use with the model, see the
    [Responsible Generative AI Toolkit][rai-toolkit].
* Transparency and Accountability:
  * This model card summarizes details on the models' architecture,
    capabilities, limitations, and evaluation processes.
  * A responsibly developed open model offers the opportunity to share
    innovation by making LLM technology accessible to developers and researchers
    across the AI ecosystem.

Risks identified and mitigations:

* Perpetuation of biases: It's encouraged to perform continuous monitoring
  (using evaluation metrics, human review) and the exploration of de-biasing
  techniques during model training, fine-tuning, and other use cases.
* Generation of harmful content: Mechanisms and guidelines for content safety
  are essential. Developers are encouraged to exercise caution and implement
  appropriate content safety safeguards based on their specific product policies
  and application use cases.
* Privacy violations: Models were trained on data filtered for removal of PII
  (Personally Identifiable Information). Developers are encouraged to adhere to
  privacy regulations with privacy-preserving techniques.

</details>


## Acknowledgement
We would like to express our gratitude to the following institutions for their contributions to this work: École Polytechnique, LINAGORA and KTH Royal Institute of Technology. Additionally, we extend our thanks to the AtlasIA community.