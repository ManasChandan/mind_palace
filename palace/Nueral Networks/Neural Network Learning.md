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

### **6. Stochastic Gradient Descent (SGD)**
For large datasets, calculating the gradient using *all* data points ($n$) for every step is computationally too expensive.
*   **The Solution:** Instead of the full dataset, the algorithm uses a small, random sample called a **minibatch** (e.g., 32 observations) to estimate the gradient.
*   **Benefits:**
    1.  **Efficiency:** It processes manageable chunks of data regardless of total dataset size.
    2.  **Escaping Minima:** The approximation introduces "noise" to the gradient path, which can help the algorithm jump out of local minima that might trap standard gradient descent.
*   **Adam Optimizer:** The course specifically uses **Adam**, a popular variation of SGD, as the default optimizer.

![x](app/static/neural_netwrok_building_blocks.png)


### **Summary of the Training Loop**
The lecture concludes by summarizing the iterative training flow:
1.  **Forward Pass:** Input data flows through layers to generate a prediction.
2.  **Loss Calculation:** The prediction is compared to the true target using the loss function.
3.  **Backprop:** The optimizer calculates the gradient of the loss with respect to the weights.
4.  **Update:** Weights are updated using the gradient and learning rate.
5.  **Repeat:** This cycle repeats for minibatches until the model is trained.