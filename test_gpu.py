
import torch
import time

device = torch.device("cuda")

x = torch.randn(3000, 3000, device=device)

torch.cuda.synchronize()

start_time = time.time()

result = torch.matmul(x, x)

torch.cuda.synchronize()

end_time = time.time()

print("GPU:", torch.cuda.get_device_name(0))
print("Matrix Shape:", result.shape)
print("Execution Time:", round(end_time - start_time, 3), "seconds")

print(
    "GPU Memory Used:",
    round(torch.cuda.memory_allocated() / 1024**3, 2),
    "GB"
)

print("GPU Working Successfully!")
