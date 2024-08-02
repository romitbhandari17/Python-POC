from torchtext.datasets import AG_NEWS
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from torch.optim import AdamW
from torch.utils.data import DataLoader, Dataset

class TextDataset(Dataset):
    def __init__(self, texts, tokenizer):
        tokenizer.pad_token = tokenizer.eos_token
        self.encodings = tokenizer(texts, truncation=True, padding=True, max_length=512, return_tensors="pt")

    def __len__(self):
        return self.encodings.input_ids.size(0)

    def __getitem__(self, idx):
        # Need to shift the input_ids to create labels
        input_ids = self.encodings.input_ids[idx]
        labels = input_ids.clone()  # Clone the input_ids to use as labels
        return {"input_ids": input_ids, "labels": labels}

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("gpt2")
model = AutoModelForCausalLM.from_pretrained("gpt2")
tokenizer.pad_token = tokenizer.eos_token  # Ensure tokenizer has a padding token

# Place the model on the correct device
device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)

optimizer = AdamW(model.parameters())

# Prepare data
train_iter = AG_NEWS(split='train')
texts = [text for _, text in train_iter]
train_dataset = TextDataset(texts, tokenizer)
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

# Training loop
model.train()
for epoch in range(50):
    for batch in train_loader:
        batch = {k: v.to(device) for k, v in batch.items()}  # Ensure batch is on the correct device
        outputs = model(**batch)
        loss = outputs.loss
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

# Generate text
prompt = tokenizer("Write a summary of the new features in the latest release of the Julia Programming Language", return_tensors="pt")
prompt = {k: v.to(device) for k, v in prompt.items()}
generated = model.generate(**prompt)
generated_text = tokenizer.decode(generated[0])

# Save generated text
with open("generated.txt", "w") as f:
    f.write(generated_text)


