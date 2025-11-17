# -*- coding: utf-8 -*-

from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

model_name = "HooshvareLab/bert-fa-base-uncased-sentiment-snappfood"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

nlp = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

text = "این محصول فوق‌العاده بود و خیلی راضی‌ام."
# text = "این محصول اصلا در حد انتظار نبود."
# text = "این محصول نه خوبه نه بد."

print(nlp(text))