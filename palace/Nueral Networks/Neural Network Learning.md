Inspired From - [MIT OpenCourseWare](https://ocw.mit.edu/courses/15-773-hands-on-deep-learning-spring-2024/)

My Notebook - [Deep Learning Intro](https://github.com/ManasChandan/deep-learning-series/blob/master/Deep_Learning_1.ipynb)

### **1. Neural Network Design: Strategy and Case Study**

**Design Philosophy**
The lecture establishes a distinction between fixed constraints and design choices. While the input layer (determined by data) and output layer (determined by the prediction task) are fixed, the "middle" of the network is up to the designer.
*   **Hidden Layers:** The user must choose the number of hidden layers and the number of neurons per layer.
*   **Rule of Thumb:** Start with the simplest network possible (e.g., one hidden layer). If it works, stop; if not, incrementally add complexity to avoid overfitting.
*   **Default Activation:** For hidden layers, the ReLU (Rectified Linear Unit) function is the standard recommendation.

**Case Study: Predicting Heart Disease**
The lecture introduces a tabular dataset from the Cleveland Clinic. The objective is to predict whether a patient will be diagnosed with heart disease within the next year based on non-cardiac visit data.
*   **Data Structure:** The dataset contains demographic data (Age, Sex) and biomarkers (Cholesterol, Blood Pressure). While there are 13 variables, the input shape is 29 because categorical variables (like chest pain type) are one-hot encoded.
*   **Architecture:**
    *   **Input Layer:** 29 neurons ($x_1$ to $x_{29}$).
    *   **Hidden Layer:** A single dense layer with 16 neurons using ReLU activation. The instructor selected 16 via trial and error, noting that higher numbers led to overfitting.
    *   **Output Layer:** A single neuron using the **Sigmoid** activation function to output a probability between 0 and 1 (binary classification).
*   **Parameter Calculation:** The network is fully connected ("dense"). The total parameter count is calculated as:
    $$(29 \text{ inputs} \times 16 \text{ weights}) + 16 \text{ biases} + (16 \text{ hidden} \times 1 \text{ output}) + 1 \text{ bias} = 497 \text{ parameters}$$
    This calculation highlights how parameters explode as layers are added.

### **2. Implementation in Keras**
The instructor demonstrates how to translate the visual architecture into code using Keras. The definition requires only four lines:
1.  **Input Definition:** `input = keras.Input(shape=29)` defines the expected shape of the data vector.
2.  **Hidden Layer:** `h = keras.layers.Dense(16, activation='relu')(input)` creates a fully connected layer with 16 nodes and connects it to the input.
3.  **Output Layer:** `output = keras.layers.Dense(1, activation='sigmoid')(h)` connects the hidden layer to the final output node.
4.  **Model Creation:** `model = keras.Model(input, output)` formally groups the layers into a trainable object.

### **3. The Mathematics of Training: Loss Functions**
Training is defined as finding the specific weights ($w$) and biases that minimize the "discrepancy" between predictions and actual values. This discrepancy is quantified by a **Loss Function**.

*   **Regression vs. Classification:**
    *   For regression (numerical output), the standard loss function is Mean Squared Error (MSE).
    *   For binary classification (0 or 1 output), MSE is inappropriate. The lecture introduces **Binary Cross-Entropy**.
*   **Deriving Binary Cross-Entropy:**
    *   **Case $y=1$ (Disease):** If the true value is 1, the loss should be 0 if the prediction is 1, and very high if the prediction approaches 0. This is modeled by $-\log(\text{predicted probability})$.
    *   **Case $y=0$ (No Disease):** If the true value is 0, the loss should be high if the prediction approaches 1. This is modeled by $-\log(1 - \text{predicted probability})$.
    *   **Combined Formula:** These are combined into a single mathematical expression to avoid conditional statements:
        $$\text{Loss} = -[y_i \log(\hat{y}_i) + (1-y_i) \log(1-\hat{y}_i)]$$
        This formula (averaged across all data points) is the Binary Cross-Entropy loss function.

### **4. Optimization: Gradient Descent**
To minimize the loss function, the course introduces **Gradient Descent**, an algorithm invented by Cauchy in 1847.

*   **The Derivative Intuition:** The derivative (gradient) at any point tells us the slope.
    *   **Positive Slope:** Increasing the weight $w$ increases the loss (so we should decrease $w$).
    *   **Negative Slope:** Increasing the weight $w$ decreases the loss (so we should increase $w$).
*   **The Algorithm:** We update weights in the opposite direction of the gradient:
    $$w_{new} = w_{old} - \alpha \times \nabla g(w)$$
    Here, $\alpha$ is the **learning rate**, a small number (e.g., 0.01) that ensures we take small steps to avoid overshooting.
*   **Multivariable Generalization:** In deep learning, loss functions have billions of parameters. We calculate the partial derivative for each weight, stack them into a vector called the **gradient** ($\nabla$), and update all weights simultaneously.

### **5. Backpropagation and Hardware**
To perform gradient descent, the gradient must be calculated efficiently.
*   **Backprop:** "Backprop" (Backpropagation) is an algorithm that applies the chain rule to the layer-by-layer architecture of neural networks. It organizes computation as a graph, calculating gradients from the output layer backward. This avoids redundant calculations.
*   **GPUs:** Backpropagation relies heavily on matrix multiplications. GPUs (Graphics Processing Units), originally designed for video game rendering, are mathematically optimized for these operations, making them essential for modern deep learning.

Backpropagation starts from the end because of the **Chain Rule** in calculus. To figure out how much a specific weight early in the network should change, you first need to know how the final error changed relative to the output.

#### 1. The Mathematical Necessity

In a neural network, the loss  is a function of the output, which is a function of the last layer, which is a function of the layer before it, and so on. To find the gradient of the loss with respect to an early weight , we use the chain rule:

By starting at the end (), we calculate that value **once** and pass it backward. If we started from the front, we would end up recalculating the same downstream derivatives thousands of times for every single weight.

#### 2. Efficiency (Dynamic Programming)

Starting from the end is a form of **dynamic programming**.

* **The "Gradient" is a signal:** As you move backward, you store the intermediate gradients.
* **Reuse:** The gradient at layer  is used to calculate the gradients for all weights in layer .

If you tried to do this "forward-prop style" (Forward Mode Differentiation), it would be computationally massive for networks with millions of parameters because you'd have to track how every single weight affects every single neuron in the next layer simultaneously.

#### 3. The "Signal" Analogy

* **Forward Pass:** We combine inputs to see what the "guess" is.
* **Backward Pass:** We compare the "guess" to the "truth."

Since the "truth" (the label) only interacts with the very last layer of the network, that is the only place where the **error signal** is born. We then flow that signal backward through the paths that created it.

#### Comparison at a Glance

| Feature | Forward Pass | Backward Pass |
| --- | --- | --- |
| **Direction** | Input  Output | Output  Input |
| **Purpose** | Prediction / Inference | Learning / Optimization |
| **Key Math** | Matrix Multiplication | Chain Rule |
| **Dependency** | Needs Input Data | Needs the Loss (Error) |

![x](app/static/backprop_re_calculation.png)


### **6. Stochastic Gradient Descent (SGD)**
For large datasets, calculating the gradient using *all* data points ($n$) for every step is computationally too expensive.
*   **The Solution:** Instead of the full dataset, the algorithm uses a small, random sample called a **minibatch** (e.g., 32 observations) to estimate the gradient.
*   **Benefits:**
    1.  **Efficiency:** It processes manageable chunks of data regardless of total dataset size.
    2.  **Escaping Minima:** The approximation introduces "noise" to the gradient path, which can help the algorithm jump out of local minima that might trap standard gradient descent.
*   **Adam Optimizer:** The course specifically uses **Adam**, a popular variation of SGD, as the default optimizer.

![x](app/static/neural_netwrok_building_blocks.png)

### **7. Advanced Training Dynamics**

**Epochs: The Full Training Cycle**
An **epoch** is one complete pass through the entire training dataset. Since neural networks learn incrementally, a single epoch is rarely enough to minimize the loss; models typically require dozens or hundreds of epochs to converge.

**Stochastic Gradient Descent (SGD) & Adam**

* **SGD & Epoch Counting:** In SGD, we update weights after processing each **minibatch** (a small random sample, e.g., 32 rows). An epoch is completed once the model has seen every minibatch in the dataset exactly once.
* **Adam (Adaptive Moment Estimation):** While SGD uses a fixed learning rate (), **Adam** is an advanced optimizer that adapts the learning rate for each individual weight. It is effectively "SGD with momentum and adaptive scaling," making it the industry standard for faster and more stable convergence.

**Regularization and Management: Callbacks**

* **Callbacks:** These are utilities that perform actions at various stages of training (e.g., at the end of an epoch).
* **Early Stopping:** A specific callback that monitors the validation loss. If the loss stops improving for a set number of epochs, training is halted to prevent overfitting and save time.
* **Dropout:** A regularization technique where a random percentage of neurons are "ignored" during each training step. This prevents the network from becoming overly reliant on specific paths, forcing it to learn more robust features.

---

### **8. Specialized Loss Functions**

**Binary vs. Categorical Cross-Entropy**

The core problem these loss functions solve is how to mathematically penalize a "wrong" probability. In classification, we aren't just looking for the right answer; we are looking for **confidence** in that answer.

**The Problem with Mean Squared Error (MSE) for Classification**

While MSE is perfect for regression, it fails in classification for two main reasons:

* **Vanishing Gradients:** The Sigmoid and Softmax functions become very "flat" as they approach 0 or 1. If the model is confidently wrong (e.g., predicting 0.99 for a 0 label), the MSE gradient becomes so small that the model stops learning.
* **Non-Convexity:** Using MSE with a Sigmoid activation creates a "bumpy" loss surface with many local minima, making it difficult for Gradient Descent to find the global minimum.

**Binary Cross-Entropy (BCE)**

BCE is designed to heavily penalize predictions that are "confident but wrong" using logarithmic curves.

* **The Logarithmic Penalty:** * If the true label is , the loss is . As the prediction  approaches 0, the loss approaches **infinity**.
* If the true label is , the loss is . As the prediction  approaches 1, the loss approaches **infinity**.

* **The Combined Formula:** To allow a single line of code to handle both cases without `if/else` logic, we use:

* If , the second term  becomes 0, leaving only the first term.
* If , the first term  becomes 0, leaving only the second term.

**Transitioning to Multi-Class: Categorical Cross-Entropy (CCE)**

When moving from 2 classes (Heart Disease vs. No Heart Disease) to  classes (e.g., Apple vs. Banana vs. Orange), the logic "rolls back" into a summation.

1. **From Sigmoid to Softmax:** In binary, we use one neuron with a Sigmoid (0 to 1). In multi-class, we use  neurons with a **Softmax** activation. Softmax ensures that all output probabilities across all classes sum exactly to 1.0 (e.g., 0.7 Apple, 0.2 Banana, 0.1 Orange).
2. **The CCE Formula:** Instead of checking , we sum the log-loss for every class :


3. **One-Hot Encoding Interaction:** In practice, since  is **One-Hot Encoded** (meaning  is 1 for the correct class and 0 for all others), the summation ignores all classes except the "True" one.
> **Example:** If the true fruit is an Apple (), the loss is simply . The model is essentially told: "I only care about how much probability you assigned to the correct answer; the higher it is, the lower the loss".

**Regression Example**

In regression-based problems, the goal is to predict a continuous numerical value rather than a discrete class. Because of this, the design of the activation functions—particularly in the output layer—differs significantly from classification tasks.


**Activation Functions in Regression**

* **Hidden Layers:** For the intermediate (hidden) layers of a regression network, the **ReLU (Rectified Linear Unit)** function remains the standard recommendation and default choice.
* **Output Layer:** The activation function in the final layer is determined by the specific range and nature of the numerical value you are trying to predict.


**The Linear Function at the Output Layer**

The most common "function" used at the end of a regression network is the **Linear Activation Function** (also known as the "identity" function).

* **Definition:** A linear activation simply passes the weighted sum of the inputs and the bias directly to the output without transformation: .
* **Purpose:** It allows the model to output any real number, ranging from negative infinity to positive infinity.
* **When to Use:** Use a linear activation (or no activation function at all, which defaults to linear in Keras/TensorFlow) when your target variable is an unbounded continuous value, such as predicting a temperature, a stock price, or a physical measurement.


**Other Output Layer Scenarios**

While the linear function is the standard, other functions are used if the output must be constrained:

* **Sigmoid:** If your regression target is strictly bounded between **0 and 1** (e.g., predicting a percentage or a probability-like score).
* **ReLU:** If your output must be **non-negative** (0 or higher) but has no upper limit (e.g., predicting the count of items or an absolute distance).
* **Softplus:** A smooth version of ReLU that is often used when you need a non-negative output that is differentiable everywhere, frequently used in predicting variances or standard deviations.

---

### **9. The TensorFlow Ecosystem**

**Tensors and Frameworks**

* **Tensors:** The fundamental data structure in Deep Learning. Tensors are multi-dimensional arrays (0D = scalar, 1D = vector, 2D = matrix, 3D+ = tensor) that can be processed efficiently on GPUs.
* **TensorFlow:** An end-to-end open-source platform for machine learning developed by Google.
* **Keras:** The high-level API for TensorFlow that allows for fast, human-readable model prototyping.

**The 3 Ways to Build Models in Keras**

1. **Sequential API:** The simplest method where layers are stacked in a plain list (one input, one output).
2. **Functional API:** Used for complex models with multiple inputs, multiple outputs, or shared layers. (Example: `output = Dense(1)(h)`).
3. **Model Subclassing:** The most flexible "Pythonic" approach where you define the forward pass manually inside a class, used primarily for custom research and complex logic.


### **Summary of the Training Loop**
The lecture concludes by summarizing the iterative training flow:
1.  **Forward Pass:** Input data flows through layers to generate a prediction.
2.  **Loss Calculation:** The prediction is compared to the true target using the loss function.
3.  **Backprop:** The optimizer calculates the gradient of the loss with respect to the weights.
4.  **Update:** Weights are updated using the gradient and learning rate.
5.  **Repeat:** This cycle repeats for minibatches until the model is trained.