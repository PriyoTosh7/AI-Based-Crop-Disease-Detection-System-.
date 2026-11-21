"""Smoke-test the configured ImageFolder DataLoaders."""
from src.training.dataset_loader import train_loader, val_loader, test_loader, class_names

if __name__ == "__main__":
    print("Classes:", len(class_names))
    print("Train batches:", len(train_loader))
    print("Validation batches:", len(val_loader))
    print("Test batches:", len(test_loader))
    images, labels = next(iter(train_loader))
    print("First batch:", tuple(images.shape), tuple(labels.shape))
