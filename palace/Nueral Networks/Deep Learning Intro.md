# Introduction to Neural Networks and Deep Learning: A Lecture Summary

I recently watched an introductory lecture from MIT OpenCourseWare on the fundamentals of Neural Networks and Deep Learning. The session covered the historical evolution of AI, the transition from traditional machine learning to deep learning, and the mathematical architecture that powers these systems. Here is a summary of what I learned.

---

<div class="toc-container"> <div class="toc-header">Table of Contents</div> <ul> <li><a href="#introduction-to-neural-networks-and-deep-learning-a-lecture-summary">Introduction</a></li> <li> <a href="#a-brief-history-of-ai">1. A Brief History of AI</a> <ul> <li><a href="#1-traditional-ai-and-polanyis-paradox">Traditional AI and Polanyi’s Paradox</a></li> <li><a href="#2-the-shift-to-machine-learning-ml">The Shift to Machine Learning (ML)</a></li> <li><a href="#3-deep-learning-automating-representation">Deep Learning: Automating Representation</a></li> <li><a href="#4-generative-ai">Generative AI</a></li> </ul> </li> <li> <a href="#the-architecture-of-neural-networks">2. The Architecture of Neural Networks</a> <ul> <li><a href="#from-logistic-regression-to-networks">From Logistic Regression to Networks</a></li> <li><a href="#the-neuron-and-activation-functions">The "Neuron" and Activation Functions</a></li> <li><a href="#network-terminology">Network Terminology</a></li> </ul> </li> <li><a href="#building-a-simple-network">3. Building a Simple Network</a></li> <li><a href="#conclusion">4. Conclusion</a></li> </ul> </div>

## A Brief History of AI

The field of AI originated at a conference in Dartmouth in 1956, where pioneers like Marvin Minsky, John McCarthy, and Claude Shannon defined the field. While the founders were optimistic that AI would be "substantially solved" quickly, it has actually taken nearly 70 years to reach our current state, progressing through three seminal breakthroughs: the traditional approach, machine learning, and finally, deep learning and generative AI.

### 1. Traditional AI and Polanyi’s Paradox

The first approach to AI relied on encoding explicit rules. If researchers wanted a computer to play chess or interpret an ECG, they would interview experts to extract "if-then" rules and program them into the system. While commonsensical, this approach failed to be pervasively successful for two reasons.

First, these rules were brittle and could not generalize to the infinite number of edge cases in the real world. Second, and more interestingly, this approach hit **Polanyi’s Paradox**: we know more than we can tell. For example, I can instantly tell the difference between a cat and a dog, but if I try to articulate exactly *how* I do it, I cannot write a rule set that a computer can use. Because we cannot articulate our own internal rules, we cannot program them explicitly.

### 2. The Shift to Machine Learning (ML)

To solve this, the field shifted to Machine Learning. Instead of telling the computer *what* to do, we give it inputs and outputs (e.g., chess positions and moves) and use statistical techniques to learn the mapping function.

However, traditional ML has a major limitation: it requires **structured data**. The data must be renderable into rows and columns of a spreadsheet. If I want to classify an image (unstructured data), the raw pixel values (0–255) have no intrinsic meaning related to the object. To make ML work, humans historically had to perform "feature engineering," manually creating representations (like measuring beak length to classify birds). This manual representation became a massive human bottleneck.

### 3. Deep Learning: Automating Representation

Deep Learning (DL) sits inside the field of Machine Learning but solves the structured data problem. The core breakthrough of DL is that it **automatically learns the right representations** from raw inputs. It creates a pipeline where raw data enters, representations are learned automatically, and a simple linear model effectively makes the final prediction. This ability to handle unstructured data stems from the confluence of new algorithms, massive data, and parallel computing hardware (GPUs).

I learned that we can view every sensor in the world—cameras, microphones, etc. as a receptacle for unstructured data. By attaching a deep learning system behind these sensors, we can analyze, classify, and predict, enabling technologies like FaceID, medical imaging diagnostics, and self-driving cars.

### 4. Generative AI

While traditional deep learning focuses on consuming unstructured data to predict numbers or categories, **Generative AI** allows us to *create* unstructured data (images, text, audio). We are seeing a rapid shift toward **multimodal models**, where sequences of text and images can be interchanged as inputs and outputs, effectively merging what used to be separate disciplines.

## The Architecture of Neural Networks

To understand how deep learning works, I looked at the "neuron." The lecture utilized a comparison to logistic regression to explain the mechanics.

### From Logistic Regression to Networks

In standard logistic regression, we take inputs (like GPA and experience), multiply them by coefficients, add an intercept, and run the result through a sigmoid function to get a probability. In the world of neural networks, we simply rename these parameters: coefficients become **weights** and intercepts become **biases**.

By drawing this process as a network graph, we realize we don't have to go directly from input to output; we can insert intermediate steps. We can stack layers of linear functions to compress and transform the data, giving the network the capacity to learn interesting representations.

### The "Neuron" and Activation Functions

A "node" or "neuron" in this network consists of two steps:

1. **Linear Function:** A weighted sum of inputs plus a bias.
2. **Activation Function:** A nonlinear function applied to that sum.

Nonlinearity is crucial; without it, the network would just be one big linear function. Common activation functions include:

* **Sigmoid:** Useful for the output layer when predicting probabilities (0 to 1).
* **ReLU (Rectified Linear Unit):** The "hero of deep learning." It outputs the input if positive, and 0 if negative. It is the default choice for hidden layers.

### Network Terminology

* **Input Layer:** The raw data.
* **Hidden Layers:** The stack of layers between input and output where the "magic" happens.
* **Output Layer:** The final prediction.
* **Dense/Fully Connected:** When every neuron in one layer connects to every neuron in the next.

Deep Learning is essentially just a neural network with many hidden layers (like ResNet).

## Building a Simple Network

I walked through an example of predicting whether a candidate gets a job interview based on two inputs (GPA and Experience).

* **Architecture:** 2 Inputs → 1 Hidden Layer (3 neurons with ReLU) → 1 Output (Sigmoid).
* **Parameter Count:** In a network with 2 inputs connecting to 3 neurons, plus a final output neuron, we have to count all weights and biases. For this small example, there are 13 total parameters (weights + biases) to learn.

The complexity arising from these layers and nonlinearities allows the network to perform "magic" compared to simple regression. This specific type of network, where data flows strictly from left to right, is called a **Feedforward Neural Network**.

## Conclusion

Deep learning has demolished the human bottleneck of manual feature engineering, allowing computers to see, hear, and generate content by learning their own representations of the world. Whether it's a Transformer or a Convolutional Neural Network, the underlying principle remains the architecture of layers, weights, biases, and activation functions.
