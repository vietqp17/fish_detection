model.eval()
with torch.no_grad():
    predictions = model([image.to(device)])

boxes = predictions[0]['boxes']
scores = predictions[0]['scores']
