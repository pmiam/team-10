# Microscope Operator

This operator initiates a microscope server and serves the same image every 60 seconds. In production, we would provide the real microscope with directions on where to go from the downstream operators.

This operator is connected to an image segmentation operator. It wraps metadata into a json-serialized string as a header, and data as bytes.