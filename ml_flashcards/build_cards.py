#!/usr/bin/env python3
"""Reproducible generator for the ML/neural-network history deck (cards.json).

Content is the chronological evolution of architectures, emphasizing the
LIMITATION of each design that prompted the next innovation:
  Foundations -> CNNs/RNNs/LSTMs/GRUs -> Embeddings/Attention/VectorDBs
  -> Transformers/LLMs/GPT-3/Claude/Claude Code.

Each tuple: (difficulty, headline, prompt_a, answer_b, notes, [tags], year)
"""
import json, re

CATEGORIES = [
    {"id": "foundations",      "label": "Foundations",
     "instruction": "From ML basics to deep neural nets"},
    {"id": "vision_sequence",  "label": "Vision & Sequence",
     "instruction": "CNNs, RNNs, LSTMs & GRUs"},
    {"id": "representations",  "label": "Representations & Retrieval",
     "instruction": "Embeddings, attention & vector search"},
    {"id": "transformers_llms","label": "Transformers & LLMs",
     "instruction": "Transformers, GPT-3, Claude & agents"},
]

DECK = {

# =====================================================================
"foundations": [
# ---- L1 canonical ----
(1,"Foundations — Artificial Intelligence","The broad field of building machines that perform tasks normally requiring human intelligence.","Artificial Intelligence (AI)","Coined at the 1956 Dartmouth workshop; machine learning and deep learning are nested subfields within it.",["history","ai","basics"],1956),
(1,"Foundations — Machine Learning","Subfield where systems learn patterns from data instead of following hand-coded rules.","Machine Learning","Arthur Samuel popularized the term in 1959; the shift from explicit rules to learned parameters is its defining idea.",["ml","basics"],1959),
(1,"Foundations — Deep Learning","Machine learning using neural networks with many stacked layers that learn features automatically.","Deep Learning","'Deep' refers to the number of layers; depth lets the model learn a hierarchy of features rather than relying on hand-engineering.",["dl","basics"],2006),
(1,"Foundations — Neural Network","A model of interconnected nodes ('neurons') loosely inspired by the brain that maps inputs to outputs.","Neural Network","Each connection has a weight; learning means adjusting those weights to reduce error.",["nn","basics"],1958),
(1,"Foundations — Neuron / Node","The basic unit that sums weighted inputs, adds a bias, and applies an activation function.","Artificial Neuron","Also called a node or unit; stacking many of them in layers builds a network.",["nn","basics"],1943),
(1,"Foundations — Training","The process of feeding examples to a model and adjusting its weights to reduce error.","Training","Contrast with inference, where the trained model is used to make predictions.",["ml","basics"],1958),
(1,"Foundations — Supervised Learning","Learning from labeled examples, mapping inputs to known correct outputs.","Supervised Learning","The dominant paradigm for classification and regression; needs labeled data.",["ml","basics"],1990),
(1,"Foundations — Parameters / Weights","The learnable numbers inside a network that get tuned during training.","Parameters (Weights)","Modern LLMs have billions of these; their count is a rough proxy for model capacity.",["nn","basics"],1958),
(1,"Foundations — GPU Acceleration","The hardware breakthrough that made training large deep networks practical via massive parallelism.","GPUs","Originally for graphics, GPUs excel at the matrix math of neural nets; their use was key to the 2012 deep-learning boom.",["hardware","dl"],2012),
(1,"Foundations — The 2012 Turning Point","The ImageNet-winning network that ignited the modern deep-learning era.","AlexNet","Krizhevsky, Sutskever & Hinton's deep CNN crushed the 2012 ImageNet benchmark, proving deep nets + GPUs work at scale.",["dl","milestone"],2012),
(1,"Foundations — Inference","Using an already-trained model to make a prediction on new input.","Inference","Distinct from training; most production cost in LLMs comes from inference at scale.",["ml","basics"],1958),
(1,"Foundations — Dataset","The collection of examples a model learns from.","Dataset","Quality, size and diversity of data often matter more than model tweaks.",["ml","basics"],1990),

# ---- L2 textbook ----
(2,"Foundations — Perceptron","Rosenblatt's 1958 single-layer learning device, the earliest trainable neural model.","Perceptron","It could only learn linearly separable functions — a limit exposed in 1969 that stalled the field.",["history","nn"],1958),
(2,"Foundations — Activation Function","The nonlinearity applied to a neuron's weighted sum, letting networks model nonlinear relationships.","Activation Function","Without it, stacked layers collapse into a single linear map; examples include sigmoid, tanh and ReLU.",["nn","basics"],1986),
(2,"Foundations — ReLU","The activation f(x)=max(0,x) that became the default in deep networks.","ReLU (Rectified Linear Unit)","Cheap to compute and avoids the saturation that plagued sigmoids, easing the vanishing-gradient problem.",["nn","activation"],2011),
(2,"Foundations — Backpropagation","The algorithm that computes gradients by propagating error backward through the layers.","Backpropagation","Popularized in 1986 by Rumelhart, Hinton & Williams; it makes training multilayer nets feasible.",["training","history"],1986),
(2,"Foundations — Gradient Descent","Iteratively nudging weights in the direction that most reduces the loss.","Gradient Descent","The workhorse optimizer; the gradient says which way is downhill on the loss surface.",["training"],1986),
(2,"Foundations — Loss Function","The measurable objective the model tries to minimize during training.","Loss Function","Examples: mean squared error for regression, cross-entropy for classification.",["training"],1990),
(2,"Foundations — Hidden Layer","A layer between input and output whose activations are learned intermediate features.","Hidden Layer","Adding hidden layers let networks solve nonlinear problems the perceptron could not.",["nn"],1986),
(2,"Foundations — Multilayer Perceptron","A fully connected feedforward network with one or more hidden layers.","Multilayer Perceptron (MLP)","Combined with backprop, the MLP overcame the single-perceptron's linear limitation.",["nn"],1986),
(2,"Foundations — Overfitting","When a model memorizes training data and fails to generalize to new data.","Overfitting","Signaled by low training error but high validation error; combated with regularization and more data.",["training"],1995),
(2,"Foundations — Bias Term","The learnable offset added to a neuron's weighted sum before activation.","Bias","Lets the activation shift left or right, independent of the inputs.",["nn"],1958),
(2,"Foundations — Epoch","One full pass of the training algorithm over the entire dataset.","Epoch","Training usually takes many epochs; too many can cause overfitting.",["training"],1990),
(2,"Foundations — Learning Rate","The step size controlling how far weights move on each gradient update.","Learning Rate","Too high diverges, too low crawls; arguably the most important hyperparameter.",["training"],1990),

# ---- L3 synthesis ----
(3,"Foundations — Vanishing Gradient","The problem where gradients shrink toward zero in deep nets, stalling learning in early layers.","Vanishing Gradient Problem","Caused by repeatedly multiplying small derivatives (e.g. from sigmoids); it motivated ReLU, careful init and normalization.",["training","limitation"],1991),
(3,"Foundations — Dropout","Randomly zeroing a fraction of activations during training to prevent co-adaptation.","Dropout","Introduced by Srivastava & Hinton (2014); acts like training an ensemble and reduces overfitting.",["regularization"],2014),
(3,"Foundations — Universal Approximation","The theorem stating a network with one hidden layer can approximate any continuous function.","Universal Approximation Theorem","Proved by Cybenko (1989) and Hornik (1991); it justifies networks in principle but says nothing about learnability or efficiency.",["theory"],1989),
(3,"Foundations — Softmax","The function that turns a vector of scores into a probability distribution over classes.","Softmax","Used at the output of classifiers and in attention; exponentiates and normalizes the logits.",["nn","math"],1989),
(3,"Foundations — Cross-Entropy Loss","The loss measuring the gap between predicted and true probability distributions.","Cross-Entropy","Standard for classification and language modeling; penalizes confident wrong predictions heavily.",["training"],1990),
(3,"Foundations — Stochastic Gradient Descent","Updating weights using small random mini-batches rather than the full dataset each step.","Stochastic Gradient Descent (SGD)","Faster and noisier than full-batch descent; the noise can even help escape poor minima.",["training"],1998),
(3,"Foundations — Sigmoid Saturation","Why sigmoid/tanh units stop learning when their inputs are large in magnitude.","Saturation","Flat tails give near-zero gradients, feeding the vanishing-gradient problem — a key reason ReLU replaced them.",["activation","limitation"],1991),
(3,"Foundations — Regularization","Techniques that constrain a model to improve generalization, e.g. weight penalties.","Regularization","L2 (weight decay) and L1 shrink weights; dropout and early stopping are also forms of it.",["training"],1995),
(3,"Foundations — Bias–Variance Tradeoff","The tension between a model too simple to fit (high bias) and too flexible (high variance).","Bias–Variance Tradeoff","Guides model complexity choices; deep nets complicate the classic picture (see double descent).",["theory"],1992),
(3,"Foundations — Hierarchical Features","Why depth helps: each layer composes simpler features into more abstract ones.","Feature Hierarchy","Early CNN layers learn edges, later ones learn objects — depth automates feature engineering.",["dl","theory"],2012),

# ---- L4 nuanced cause/effect ----
(4,"Foundations — The XOR Problem","The simple nonlinear function a single perceptron provably cannot learn.","XOR","Minsky & Papert's 1969 'Perceptrons' highlighted this limit, helping trigger an AI winter until multilayer nets + backprop answered it.",["history","limitation"],1969),
(4,"Foundations — First AI Winter","The funding and interest collapse partly caused by the perceptron's exposed limitations.","AI Winter","Minsky & Papert (1969) showed single-layer nets can't do XOR; enthusiasm only recovered with backprop-trained multilayer nets.",["history"],1974),
(4,"Foundations — Batch Normalization","Normalizing layer inputs per mini-batch to stabilize and speed up training.","Batch Normalization","Ioffe & Szegedy (2015) let much deeper nets train reliably by reducing sensitivity to initialization and learning rate.",["training"],2015),
(4,"Foundations — Adam Optimizer","The adaptive optimizer combining momentum with per-parameter learning rates.","Adam","Kingma & Ba (2014); its robustness made it the default optimizer for most deep models.",["training"],2014),
(4,"Foundations — Exploding Gradients","When gradients grow uncontrollably large, destabilizing training (common in deep/recurrent nets).","Exploding Gradient Problem","Mitigated by gradient clipping; the flip side of the vanishing-gradient issue.",["training","limitation"],1994),
(4,"Foundations — McCulloch–Pitts Neuron","The 1943 binary threshold logic unit that first modeled a neuron mathematically.","McCulloch–Pitts Neuron","Predates the perceptron; showed networks of simple units could compute logical functions.",["history"],1943),
(4,"Foundations — Why ReLU Won","The property of ReLU that keeps gradients alive for positive inputs, unlike saturating units.","Non-saturating Gradient","Constant gradient of 1 for x>0 lets error signals flow through deep stacks, directly addressing vanishing gradients.",["activation"],2011),
(4,"Foundations — Weight Initialization","Schemes like Xavier/He that set starting weights to keep signal variance stable across layers.","Xavier / He Initialization","Poor init causes vanishing or exploding activations; principled init was a prerequisite for training very deep nets.",["training"],2010),
(4,"Foundations — Deep Belief Networks","Hinton's 2006 layer-wise pretrained nets that reignited interest in 'deep' learning.","Deep Belief Networks","Greedy unsupervised pretraining (RBMs) first made deep nets trainable, before ReLU and big data made it unnecessary.",["history","dl"],2006),

# ---- L5 scholarly ----
(5,"Foundations — Reverse-Mode Autodiff","The general technique underlying backprop, predating its 1986 popularization.","Reverse-Mode Automatic Differentiation","Linnainmaa described it in 1970 and Werbos applied it to neural nets in 1974; 'backprop' is its application to layered nets.",["history","theory"],1970),
(5,"Foundations — Credit Assignment Problem","The core difficulty of deciding which weights deserve blame for an error across many layers/timesteps.","Credit Assignment Problem","Backprop solves it spatially; recurrent nets face a temporal version that LSTMs were designed to address.",["theory"],1986),
(5,"Foundations — Double Descent","The modern phenomenon where test error falls, rises, then falls again as model size grows past the interpolation point.","Double Descent","Belkin et al. (2019) showed overparameterized nets can generalize well, complicating the classic bias–variance story.",["theory"],2019),
(5,"Foundations — Lottery Ticket Hypothesis","The conjecture that dense nets contain sparse subnetworks that train to comparable accuracy in isolation.","Lottery Ticket Hypothesis","Frankle & Carbin (2018); reframes why overparameterization helps optimization.",["theory"],2018),
(5,"Foundations — Degradation Problem","The observation that adding layers to a plain deep net can increase training error, not just overfit.","Degradation Problem","He et al. (2015) identified this and introduced residual connections (ResNet) as the fix.",["theory","limitation"],2015),
(5,"Foundations — Cybenko's Theorem","The specific 1989 proof that sigmoidal one-hidden-layer nets are universal approximators.","Cybenko (1989)","Hornik (1991) generalized it beyond sigmoids; both are existence results, silent on how to find the weights.",["theory"],1989),
(5,"Foundations — Hochreiter's 1991 Thesis","The diploma thesis that first formally analyzed why gradients vanish in deep recurrent nets.","Hochreiter (1991)","This analysis directly motivated the 1997 LSTM design with its constant error carousel.",["history","theory"],1991),
(5,"Foundations — Information Bottleneck","Tishby's theory framing learning as compressing input while preserving output-relevant information.","Information Bottleneck","Offers one lens on why deep nets generalize; remains debated as an explanation of training dynamics.",["theory"],2015),
],

# =====================================================================
"vision_sequence": [
# ---- L1 ----
(1,"Vision & Sequence — CNN","The neural architecture specialized for grid data like images.","Convolutional Neural Network (CNN)","Uses local filters and weight sharing to detect spatial patterns efficiently.",["cnn","vision"],1989),
(1,"Vision & Sequence — RNN","The architecture designed to process sequences by maintaining state across steps.","Recurrent Neural Network (RNN)","Feeds its own previous output back in, giving it a form of memory for sequential data.",["rnn","sequence"],1986),
(1,"Vision & Sequence — Filter / Kernel","The small sliding window of weights a CNN convolves across an image.","Kernel (Filter)","Each filter learns to detect one pattern, such as an edge or texture.",["cnn","vision"],1989),
(1,"Vision & Sequence — Pooling","The CNN operation that downsamples feature maps to shrink them and add robustness.","Pooling","Max pooling keeps the strongest activation in each region, reducing size and adding small-shift tolerance.",["cnn","vision"],1998),
(1,"Vision & Sequence — ImageNet","The large labeled image dataset/benchmark that drove the deep-learning vision boom.","ImageNet","AlexNet's 2012 win on it is widely seen as deep learning's breakout moment.",["vision","dataset"],2009),
(1,"Vision & Sequence — Hidden State","An RNN's running memory vector, updated at each timestep.","Hidden State","It summarizes everything seen so far and is passed to the next step.",["rnn","sequence"],1986),
(1,"Vision & Sequence — LSTM","The gated recurrent network built to remember information over long sequences.","Long Short-Term Memory (LSTM)","Hochreiter & Schmidhuber (1997); its gates and cell state fight the vanishing-gradient problem.",["rnn","sequence"],1997),
(1,"Vision & Sequence — GRU","A streamlined gated RNN with fewer gates than the LSTM.","Gated Recurrent Unit (GRU)","Cho et al. (2014); often matches LSTM performance with less computation.",["rnn","sequence"],2014),
(1,"Vision & Sequence — Sequence Data","Ordered data like text, audio or time series where order carries meaning.","Sequence","RNNs, LSTMs and GRUs were designed specifically to model it.",["sequence"],1986),
(1,"Vision & Sequence — Feature Map","The output produced when a filter is convolved across an input.","Feature Map","Stacking many feature maps lets a CNN detect many patterns in parallel.",["cnn","vision"],1989),
(1,"Vision & Sequence — Channels","The depth dimension of an image or feature map, e.g. the R, G and B of a color photo.","Channels","Each convolutional filter spans all input channels and outputs one new channel.",["cnn","vision"],1989),
(1,"Vision & Sequence — Edge Detectors","What a CNN's earliest filters reliably learn to recognize.","Edge Detectors","First-layer filters fire on edges and color blobs, the building blocks for later, complex features.",["cnn","vision"],2012),

# ---- L2 ----
(2,"Vision & Sequence — Convolution","The operation of sliding a filter over input and computing dot products.","Convolution","Reuses the same weights across all positions, slashing parameters versus a dense layer.",["cnn","vision"],1989),
(2,"Vision & Sequence — Parameter Sharing","The CNN principle of reusing one filter's weights across every spatial location.","Weight Sharing","Drastically cuts parameters and builds in the assumption that a useful pattern is useful anywhere in the image.",["cnn"],1989),
(2,"Vision & Sequence — Max Pooling","Downsampling by taking the maximum value in each local region.","Max Pooling","Provides translation tolerance and reduces computation in deeper layers.",["cnn","vision"],1998),
(2,"Vision & Sequence — LeNet-5","LeCun's pioneering CNN for handwritten digit recognition.","LeNet-5","The 1998 network demonstrated convolution+pooling+backprop on real images years before it scaled.",["cnn","history"],1998),
(2,"Vision & Sequence — AlexNet","The 2012 deep CNN that won ImageNet and launched the deep-learning era.","AlexNet","Used ReLU, dropout and two GPUs; its margin of victory convinced the field to go deep.",["cnn","milestone"],2012),
(2,"Vision & Sequence — Backprop Through Time","Backpropagation unrolled across an RNN's timesteps to compute gradients.","Backpropagation Through Time (BPTT)","Treats the unrolled sequence as a deep net; its depth in time is the source of vanishing gradients.",["rnn","training"],1990),
(2,"Vision & Sequence — Recurrence","The feedback loop that feeds an RNN's output back as input for the next step.","Recurrence","This is what gives RNNs memory but also makes them inherently sequential and slow to train.",["rnn"],1986),
(2,"Vision & Sequence — Gates","The learned valves in an LSTM/GRU that control what information is kept or discarded.","Gates","Sigmoid-controlled gates regulate the flow into and out of memory, enabling long-range retention.",["rnn"],1997),
(2,"Vision & Sequence — Seq2Seq","The encoder–decoder design that maps one sequence to another, e.g. for translation.","Sequence-to-Sequence (Seq2Seq)","Sutskever et al. (2014); an encoder compresses the input, a decoder generates the output.",["sequence","nmt"],2014),
(2,"Vision & Sequence — VGGNet","The 2014 CNN that showed depth via stacks of small 3×3 filters.","VGGNet","Simonyan & Zisserman; simple and uniform, it popularized very deep, regular architectures.",["cnn"],2014),
(2,"Vision & Sequence — Stride & Padding","The two settings that control how a filter steps across input and how borders are handled.","Stride & Padding","Stride sets the step size (and downsampling); padding preserves spatial size at the edges.",["cnn","vision"],1998),
(2,"Vision & Sequence — Data Augmentation","Expanding training data with flips, crops and color shifts to fight overfitting.","Data Augmentation","Cheap label-preserving transforms boosted CNN generalization and were central to AlexNet's win.",["cnn","training"],2012),

# ---- L3 ----
(3,"Vision & Sequence — Translation Invariance","The CNN property that a learned pattern is recognized regardless of its position.","Translation Invariance","Emerges from weight sharing plus pooling; it's why CNNs suit images so well.",["cnn","theory"],1998),
(3,"Vision & Sequence — Receptive Field","The region of the input that influences a particular neuron's activation.","Receptive Field","Grows with depth; deep CNN units 'see' large parts of the image, enabling object-level features.",["cnn","theory"],1998),
(3,"Vision & Sequence — Long-Range Dependency","The challenge of connecting information separated by many timesteps in a sequence.","Long-Range Dependency Problem","Plain RNNs forget distant context as gradients vanish over time — the motivation for LSTMs and later attention.",["rnn","limitation"],1991),
(3,"Vision & Sequence — Cell State","The LSTM's protected memory line that carries information across many steps with minimal change.","Cell State","Gates add or remove information from it; this near-linear highway is what preserves gradients.",["rnn"],1997),
(3,"Vision & Sequence — Forget Gate","The LSTM gate that decides what to erase from the cell state.","Forget Gate","Added by Gers et al. (2000); learning to forget proved crucial for handling long sequences.",["rnn"],2000),
(3,"Vision & Sequence — GRU vs LSTM","Why a GRU is often preferred despite the LSTM's longer track record.","Fewer Parameters","The GRU merges gates and drops the separate cell state, training faster with comparable accuracy.",["rnn"],2014),
(3,"Vision & Sequence — Bidirectional RNN","An RNN that reads a sequence both forward and backward.","Bidirectional RNN","Lets each position use both past and future context; common in tagging and pre-transformer NLP.",["rnn"],1997),
(3,"Vision & Sequence — Encoder–Decoder","The two-part scheme where one network reads the input and another writes the output.","Encoder–Decoder","Foundational to translation and later to transformers; the encoder's summary feeds the decoder.",["sequence"],2014),
(3,"Vision & Sequence — Skip Connection","The shortcut that adds a layer's input directly to its output.","Residual / Skip Connection","Introduced by ResNet (2015); it lets gradients flow past many layers, enabling 100+ layer nets.",["cnn"],2015),
(3,"Vision & Sequence — Gradient Clipping","Capping gradient magnitude to prevent the exploding-gradient instability in RNNs.","Gradient Clipping","A simple, standard fix that keeps recurrent training stable.",["rnn","training"],2013),

# ---- L4 ----
(4,"Vision & Sequence — ResNet's Insight","How ResNet enabled extremely deep networks despite the degradation problem.","Residual Learning","By learning F(x)+x, layers only need to learn a residual; identity shortcuts preserve gradients (He et al., 2015).",["cnn","theory"],2015),
(4,"Vision & Sequence — The Seq2Seq Bottleneck","The flaw in early encoder–decoders that compress an entire input into one fixed vector.","Fixed-Length Context Vector","Long inputs overflow this single vector, hurting translation — the limitation attention was invented to solve.",["sequence","limitation"],2014),
(4,"Vision & Sequence — Constant Error Carousel","The LSTM mechanism that lets error flow unchanged through the cell over many steps.","Constant Error Carousel (CEC)","The self-loop with weight 1 keeps gradients from vanishing — the conceptual heart of the LSTM.",["rnn","theory"],1997),
(4,"Vision & Sequence — Why CNNs Beat Dense Nets on Images","The two CNN properties that make them vastly more efficient than fully connected nets for pixels.","Local Connectivity + Weight Sharing","They exploit spatial locality and reuse filters, cutting parameters by orders of magnitude and improving generalization.",["cnn","theory"],1989),
(4,"Vision & Sequence — Teacher Forcing","Feeding the true previous token (not the model's guess) into the decoder during training.","Teacher Forcing","Speeds and stabilizes seq2seq training but can cause exposure bias at inference time.",["sequence","training"],2014),
(4,"Vision & Sequence — Sequential Bottleneck of RNNs","The structural reason RNNs are slow to train on modern hardware.","No Parallelism Across Time","Each step depends on the previous one, so timesteps can't be parallelized — a key motivation for the Transformer.",["rnn","limitation"],2017),
(4,"Vision & Sequence — Inception / GoogLeNet","The 2014 architecture using parallel multi-scale filters within a module.","Inception (GoogLeNet)","Processes features at several filter sizes at once, improving efficiency on ImageNet.",["cnn"],2014),
(4,"Vision & Sequence — Image Captioning Bridge","The task that fused a CNN encoder with an RNN decoder to describe images in words.","CNN+RNN Captioning","Show-and-Tell (2015) used a CNN to encode the image and an LSTM to generate the caption — an early multimodal pipeline.",["cnn","rnn"],2015),

# ---- L5 ----
(5,"Vision & Sequence — Neocognitron","Fukushima's 1980 hierarchical vision model that prefigured the CNN.","Neocognitron","Introduced alternating feature-extraction and pooling layers; LeCun later added backprop to make it trainable.",["cnn","history"],1980),
(5,"Vision & Sequence — LeCun 1989 Backprop-Conv","The first application of backpropagation to a convolutional network (on ZIP-code digits).","LeCun et al. (1989)","Demonstrated end-to-end learned convolutional features years before compute and data caught up.",["cnn","history"],1989),
(5,"Vision & Sequence — Identity Mapping","He et al.'s 2016 refinement showing pre-activation residual blocks ease optimization further.","Identity Mappings in ResNets","Clean identity shortcuts let signal and gradient pass untransformed, enabling 1000-layer nets.",["cnn","theory"],2016),
(5,"Vision & Sequence — Highway Networks","The 2015 gated-shortcut architecture that preceded ResNet's simpler additive shortcuts.","Highway Networks","Srivastava et al. used learned gates to carry information across depth; ResNet showed plain identity works.",["cnn","history"],2015),
(5,"Vision & Sequence — Peephole Connections","An LSTM variant letting gates inspect the cell state directly.","Peephole LSTM","Gers & Schmidhuber (2000); improved precise timing tasks, illustrating LSTM gate engineering.",["rnn"],2000),
(5,"Vision & Sequence — Dilated Convolutions","Convolutions with gaps that expand the receptive field without adding parameters.","Dilated (Atrous) Convolution","Used in WaveNet and segmentation to capture wide context cheaply.",["cnn"],2016),
(5,"Vision & Sequence — Bahdanau Attention","The 2014 mechanism that let a decoder look back at all encoder states, breaking the bottleneck.","Bahdanau Attention","This additive attention over the source sequence directly inspired the Transformer's self-attention three years later.",["sequence","attention"],2014),
(5,"Vision & Sequence — Vanishing Gradient in RNNs (Formal)","The reason error signals decay exponentially with sequence length in plain RNNs.","Repeated Jacobian Multiplication","Gradients are products of many recurrent Jacobians; eigenvalues <1 vanish, >1 explode — the CEC sidesteps this.",["rnn","theory"],1994),
],

# =====================================================================
"representations": [
# ---- L1 ----
(1,"Representations — Word Embedding","Representing a word as a dense vector of numbers that captures meaning.","Word Embedding","Similar words land near each other in the vector space, unlike arbitrary one-hot codes.",["embeddings","nlp"],2013),
(1,"Representations — Vector Database","A database that stores embeddings and retrieves the nearest vectors to a query.","Vector Database","Powers semantic search and retrieval-augmented generation for LLMs.",["vectordb","retrieval"],2019),
(1,"Representations — Semantic Search","Searching by meaning rather than exact keyword match.","Semantic Search","Compares query and document embeddings, finding relevant results even with different wording.",["retrieval","nlp"],2019),
(1,"Representations — Cosine Similarity","The common measure of how close two vectors point in the same direction.","Cosine Similarity","Ranges from -1 to 1; widely used to compare embeddings regardless of their magnitude.",["math","embeddings"],2013),
(1,"Representations — Tokenization","Splitting text into the small units a model actually processes.","Tokenization","Tokens may be words or subwords; the model reads token IDs, not raw characters.",["nlp","tokens"],2016),
(1,"Representations — Embedding Vector","The list of numbers that encodes an item's meaning in a model.","Embedding","Text, images and audio can all be embedded into a shared numeric space.",["embeddings"],2013),
(1,"Representations — Attention (Intuition)","Letting a model focus on the most relevant parts of the input when producing each output.","Attention","Instead of one fixed summary, the model dynamically weighs all inputs per step.",["attention"],2014),
(1,"Representations — Latent Space","The learned multi-dimensional space where embeddings live.","Latent Space","Directions and distances in it correspond to semantic relationships.",["embeddings","theory"],2013),
(1,"Representations — Embedding Layer","The first layer of a language model that turns each token ID into its learned vector.","Embedding Layer","A simple lookup table of vectors, trained jointly with the rest of the network.",["embeddings","nlp"],2013),
(1,"Representations — Recommendations","A classic non-text use of embeddings: representing users and items as nearby vectors.","Recommendation Embeddings","Matrix-factorization vectors for users/items predate and parallel word embeddings.",["embeddings","apps"],2009),

# ---- L2 ----
(2,"Representations — Word2Vec","Mikolov's 2013 method that learns word vectors from co-occurrence in large text.","Word2Vec","Trained by predicting context words; it popularized dense embeddings and famous analogy arithmetic.",["embeddings","nlp"],2013),
(2,"Representations — Distributional Hypothesis","The linguistic idea that words appearing in similar contexts have similar meanings.","Distributional Hypothesis","Firth's 'you shall know a word by the company it keeps' underpins all word embeddings.",["nlp","theory"],1957),
(2,"Representations — One-Hot Encoding","Representing a word as a sparse vector with a single 1 and zeros elsewhere.","One-Hot Encoding","Huge, sparse and meaningless about similarity — the limitation dense embeddings replaced.",["nlp","limitation"],2000),
(2,"Representations — King − Man + Woman","The famous analogy that word vectors solve via arithmetic, yielding 'Queen'.","Vector Analogy","Showed embeddings capture relational structure (gender, tense) as consistent directions in space.",["embeddings"],2013),
(2,"Representations — GloVe","Stanford's 2014 embeddings learned by factorizing a global co-occurrence matrix.","GloVe","Pennington et al.; an alternative to Word2Vec that uses corpus-wide statistics directly.",["embeddings","nlp"],2014),
(2,"Representations — Query, Key, Value","The three projected vectors at the heart of the attention mechanism.","Query / Key / Value","A query is matched against keys to weight the corresponding values — attention as soft lookup.",["attention"],2017),
(2,"Representations — Positional Encoding","Information added to token embeddings so a transformer knows their order.","Positional Encoding","Since self-attention is order-agnostic, position must be injected explicitly.",["attention","transformers"],2017),
(2,"Representations — Nearest Neighbor Search","Finding the stored vectors closest to a query vector.","Nearest Neighbor Search","The core operation of a vector database; done approximately at scale for speed.",["vectordb","retrieval"],2017),
(2,"Representations — Dot Product","The simplest similarity score between two vectors: multiply componentwise and sum.","Dot Product","Cosine similarity is just the dot product of normalized vectors; both rank nearest matches.",["math","embeddings"],2013),
(2,"Representations — Image Embeddings","Encoding pictures as vectors so visually or semantically similar images sit close together.","Image Embeddings","CNNs and later vision transformers produce these for search, clustering and multimodal models.",["embeddings","vision"],2014),

# ---- L3 ----
(3,"Representations — Skip-gram vs CBOW","The two Word2Vec training modes: predict context from a word, or a word from context.","Skip-gram vs CBOW","Skip-gram predicts surrounding words and handles rare words better; CBOW is faster.",["embeddings"],2013),
(3,"Representations — Contextual Embeddings","Embeddings where a word's vector depends on the sentence it appears in.","Contextual Embeddings","ELMo/BERT solved the 'bank' (river vs money) ambiguity that static Word2Vec vectors could not.",["embeddings","nlp"],2018),
(3,"Representations — Self-Attention","Attention applied within a single sequence so every token attends to every other.","Self-Attention","Lets a transformer relate any two positions directly, in one step, regardless of distance.",["attention","transformers"],2017),
(3,"Representations — Multi-Head Attention","Running several attention operations in parallel, each in a different subspace.","Multi-Head Attention","Different heads learn different relationships (syntax, coreference), then their outputs are combined.",["attention","transformers"],2017),
(3,"Representations — Scaled Dot-Product Attention","Computing attention weights as softmax of scaled query·key dot products.","Scaled Dot-Product Attention","The transformer's core formula; scaling by √dₖ keeps gradients stable.",["attention","transformers"],2017),
(3,"Representations — Approximate Nearest Neighbor","Trading exactness for speed when searching billions of vectors.","Approximate Nearest Neighbor (ANN)","Exact search is too slow at scale; ANN indexes return near-best matches in milliseconds.",["vectordb","retrieval"],2016),
(3,"Representations — Retrieval-Augmented Generation","Giving an LLM relevant retrieved documents to ground its answer.","Retrieval-Augmented Generation (RAG)","Lewis et al. (2020); pairs a vector search with generation to reduce hallucination and add fresh knowledge.",["retrieval","llm"],2020),
(3,"Representations — Subword Tokenization","Splitting rare words into reusable fragments instead of treating each word atomically.","Byte-Pair Encoding (BPE)","Handles unlimited vocabulary and misspellings with a fixed token set; standard in modern LLMs.",["tokens","nlp"],2016),
(3,"Representations — Sentence Embeddings","Encoding a whole sentence or passage as one vector for retrieval.","Sentence Embeddings","Models like Sentence-BERT produce these so semantically similar texts sit close together.",["embeddings","retrieval"],2019),
(3,"Representations — Document Chunking","Splitting long documents into passages before embedding them for retrieval.","Document Chunking","Chunk size trades context for precision; a practical linchpin of effective RAG systems.",["retrieval","rag"],2020),

# ---- L4 ----
(4,"Representations — How Attention Fixed Seq2Seq","Why attention removed the fixed-vector bottleneck in translation.","Dynamic Access to All States","The decoder weights every encoder state per output token, so long inputs no longer get crushed into one vector.",["attention","theory"],2014),
(4,"Representations — Why Scale by √dₖ","The reason scaled dot-product attention divides scores before softmax.","Prevent Saturated Softmax","Large dot products in high dimensions push softmax into tiny-gradient regions; the √dₖ factor counteracts this.",["attention","theory"],2017),
(4,"Representations — ELMo","The 2018 model giving each word a context-dependent vector from a bidirectional LSTM.","ELMo","Peters et al.; a milestone toward contextual representation, soon eclipsed by transformer-based BERT.",["embeddings","nlp"],2018),
(4,"Representations — Why Transformers Need Positions","The structural reason order must be added explicitly in a transformer.","Permutation Invariance of Attention","Self-attention treats inputs as a set; without positional encoding 'dog bites man' = 'man bites dog'.",["attention","theory"],2017),
(4,"Representations — HNSW Index","The graph-based ANN structure powering many vector databases.","Hierarchical Navigable Small World (HNSW)","Builds layered proximity graphs for fast, high-recall search; a default in tools like FAISS and pgvector.",["vectordb"],2016),
(4,"Representations — RAG Pipeline","The end-to-end flow connecting a vector store to an LLM at query time.","Embed → Retrieve → Augment → Generate","The query is embedded, top matches are fetched from the vector DB, then inserted into the prompt as context.",["retrieval","llm"],2020),
(4,"Representations — Attention as Soft Lookup","The dictionary analogy that explains what attention computes.","Soft Key-Value Retrieval","Queries softly match keys and return a weighted blend of values — a differentiable, fuzzy hash table.",["attention","theory"],2017),
(4,"Representations — Curse of Dimensionality","Why exact nearest-neighbor search degrades as embedding dimensions grow.","Curse of Dimensionality","Distances concentrate in high dimensions, making brute-force search slow and motivating ANN indexes.",["vectordb","theory"],2016),
(4,"Representations — Hybrid Search","Combining keyword (sparse) and embedding (dense) retrieval for best results.","Hybrid Search","Dense vectors catch meaning, sparse matches catch exact terms/IDs; fusing them beats either alone.",["retrieval","vectordb"],2021),

# ---- L5 ----
(5,"Representations — Negative Sampling","The Word2Vec trick that makes training tractable over huge vocabularies.","Negative Sampling","Instead of a full softmax, it contrasts true context words against a few random 'negatives' (Mikolov, 2013).",["embeddings","training"],2013),
(5,"Representations — GloVe Objective","What GloVe actually factorizes to obtain its vectors.","Log Co-occurrence Matrix","It fits vectors whose dot products match log co-occurrence counts, blending count- and prediction-based views.",["embeddings","theory"],2014),
(5,"Representations — Rotary Positional Embeddings","The 2021 method encoding position by rotating query/key vectors.","RoPE","Su et al.; encodes relative position and extrapolates to longer contexts, now common in modern LLMs.",["attention","transformers"],2021),
(5,"Representations — Product Quantization","Compressing vectors into compact codes to fit billions in memory for ANN search.","Product Quantization","Splits vectors into subspaces and quantizes each; underlies FAISS's large-scale indexes.",["vectordb","theory"],2011),
(5,"Representations — FAISS","Facebook AI's open-source library for efficient similarity search over dense vectors.","FAISS","Johnson et al. (2017); provides GPU-accelerated ANN and quantization, a backbone of many vector stores.",["vectordb"],2017),
(5,"Representations — Contrastive Learning","Training embeddings by pulling related pairs together and pushing unrelated apart.","Contrastive Learning","Powers strong sentence and multimodal embeddings (e.g. CLIP) by learning from positive/negative pairs.",["embeddings","training"],2020),
(5,"Representations — Harris Distributional Structure","The 1954 formalization of meaning-from-distribution that grounds embeddings theoretically.","Harris (1954)","Zellig Harris argued linguistic units are defined by their distribution — the statistical basis later operationalized by Word2Vec.",["nlp","history"],1954),
(5,"Representations — Cross-Attention","Attention where queries come from one sequence and keys/values from another.","Cross-Attention","The decoder-to-encoder link in transformers; the modern descendant of Bahdanau's encoder–decoder attention.",["attention","transformers"],2017),
(5,"Representations — CLIP","OpenAI's 2021 model that embeds images and text into one shared space via contrastive training.","CLIP","Trained on image–caption pairs so a photo and its description land nearby — enabling zero-shot vision and text-to-image search.",["embeddings","multimodal"],2021),
],

# =====================================================================
"transformers_llms": [
# ---- L1 ----
(1,"Transformers & LLMs — Transformer","The 2017 architecture built entirely on attention, with no recurrence.","Transformer","'Attention Is All You Need'; it parallelizes training and underlies virtually all modern LLMs.",["transformers","milestone"],2017),
(1,"Transformers & LLMs — LLM","A large neural network trained on vast text to predict and generate language.","Large Language Model (LLM)","Typically a transformer with billions of parameters trained on internet-scale text.",["llm"],2020),
(1,"Transformers & LLMs — GPT","The acronym for the decoder-only generative model family from OpenAI.","Generative Pre-trained Transformer","Trained to predict the next token, then prompted or fine-tuned for tasks.",["llm","gpt"],2018),
(1,"Transformers & LLMs — ChatGPT","The 2022 conversational app that brought LLMs to the mainstream.","ChatGPT","Built on instruction-tuned GPT models; its launch triggered the generative-AI boom.",["llm","product"],2022),
(1,"Transformers & LLMs — Claude","Anthropic's family of large language models and AI assistant.","Claude","First released in 2023; trained with Constitutional AI to be helpful, harmless and honest.",["claude","anthropic"],2023),
(1,"Transformers & LLMs — Next-Token Prediction","The simple training objective behind generative language models.","Next-Token Prediction","The model repeatedly predicts the most likely following token; fluent text emerges at scale.",["llm","training"],2018),
(1,"Transformers & LLMs — Context Window","The maximum amount of text a model can consider at once.","Context Window","Measured in tokens; larger windows let models read long documents or conversations.",["llm","tokens"],2020),
(1,"Transformers & LLMs — Anthropic","The AI safety company that builds Claude.","Anthropic","Founded in 2021 with a focus on AI safety and interpretability research.",["anthropic","claude"],2021),
(1,"Transformers & LLMs — Prompt","The input text you give a language model to elicit a response.","Prompt","Crafting effective prompts ('prompt engineering') became a core skill for using LLMs.",["llm"],2020),
(1,"Transformers & LLMs — Generative AI","The umbrella term for models that create new text, images, code or audio.","Generative AI","LLMs are its text branch; the 2022–2023 wave brought it to hundreds of millions of users.",["llm","genai"],2022),
(1,"Transformers & LLMs — Temperature","The setting that controls how random versus focused a model's word choices are.","Temperature","Low temperature gives predictable output; high temperature increases diversity and risk of nonsense.",["llm","inference"],2018),

# ---- L2 ----
(2,"Transformers & LLMs — Attention Is All You Need","The 2017 paper that introduced the Transformer.","Attention Is All You Need","Vaswani et al. dropped recurrence entirely, relying on self-attention and enabling massive parallel training.",["transformers","history"],2017),
(2,"Transformers & LLMs — BERT","Google's 2018 bidirectional transformer trained with masked language modeling.","BERT","Reads context in both directions; excelled at understanding tasks but isn't generative.",["transformers","nlp"],2018),
(2,"Transformers & LLMs — GPT-3","OpenAI's 2020 model with 175 billion parameters that showed strong few-shot ability.","GPT-3","Its scale revealed in-context learning: solving tasks from a few examples in the prompt, no fine-tuning.",["llm","gpt","milestone"],2020),
(2,"Transformers & LLMs — Pretraining","The first phase: learning general patterns from massive unlabeled text.","Pretraining","Produces a foundation model later adapted by fine-tuning or prompting.",["llm","training"],2018),
(2,"Transformers & LLMs — Fine-Tuning","Further training a pretrained model on a narrower task or dataset.","Fine-Tuning","Specializes a general model; instruction tuning and RLHF are forms of it.",["llm","training"],2018),
(2,"Transformers & LLMs — Hallucination","When an LLM confidently states plausible but false information.","Hallucination","A core reliability problem; retrieval (RAG) and better training aim to reduce it.",["llm","limitation"],2021),
(2,"Transformers & LLMs — Tokens","The units of text LLMs read and bill by.","Tokens","Roughly three-quarters of a word in English; context length and cost are measured in tokens.",["llm","tokens"],2018),
(2,"Transformers & LLMs — GPT-2","OpenAI's 2019 1.5B-parameter model, a scale-up of GPT.","GPT-2","Notable for coherent long-form generation and a staged release over misuse concerns.",["llm","gpt"],2019),
(2,"Transformers & LLMs — Foundation Model","A large model pretrained broadly and adaptable to many downstream tasks.","Foundation Model","Term coined at Stanford (2021); captures the shift from task-specific to general-purpose models.",["llm"],2021),
(2,"Transformers & LLMs — Transfer Learning","Reusing knowledge from a pretrained model on a new task instead of training from scratch.","Transfer Learning","The pretrain-then-adapt paradigm that made modern NLP data-efficient.",["llm","training"],2018),
(2,"Transformers & LLMs — T5","Google's 2019 model casting every NLP task as text-to-text.","T5 (Text-to-Text Transfer Transformer)","A unified encoder–decoder framing where inputs and outputs are always strings.",["transformers","nlp"],2019),

# ---- L3 ----
(3,"Transformers & LLMs — Decoder-Only vs Encoder-Only","The architectural split between BERT-style and GPT-style transformers.","Decoder-Only vs Encoder-Only","BERT (encoder) reads bidirectionally for understanding; GPT (decoder) predicts left-to-right for generation.",["transformers","theory"],2018),
(3,"Transformers & LLMs — In-Context Learning","Solving a task from examples in the prompt, without updating weights.","In-Context Learning","Emerged prominently with GPT-3; the model adapts at inference time from the prompt alone.",["llm"],2020),
(3,"Transformers & LLMs — Scaling Laws","The finding that loss falls predictably as model size, data and compute grow.","Scaling Laws","Kaplan et al. (2020) showed smooth power-law improvements, justifying ever-larger models.",["llm","theory"],2020),
(3,"Transformers & LLMs — RLHF","Aligning a model to human preferences using a learned reward signal.","Reinforcement Learning from Human Feedback (RLHF)","Humans rank outputs to train a reward model, then the LLM is optimized against it — key to ChatGPT/Claude usability.",["llm","alignment"],2022),
(3,"Transformers & LLMs — Instruction Tuning","Fine-tuning a model to follow natural-language instructions.","Instruction Tuning","InstructGPT (2022) showed it makes raw LLMs far more helpful and controllable.",["llm","alignment"],2022),
(3,"Transformers & LLMs — Autoregressive Generation","Producing text one token at a time, each conditioned on all previous tokens.","Autoregressive Generation","The decoding scheme of GPT-style models; tokens are sampled sequentially.",["llm","theory"],2018),
(3,"Transformers & LLMs — Emergent Abilities","Capabilities that appear only once models pass a certain scale.","Emergent Abilities","Skills like arithmetic or multi-step reasoning seem to switch on with scale, though the framing is debated.",["llm","theory"],2022),
(3,"Transformers & LLMs — Constitutional AI","Anthropic's method of aligning a model using a written set of principles.","Constitutional AI","The model critiques and revises its own outputs against a 'constitution', reducing reliance on human-labeled harm data.",["claude","alignment"],2022),
(3,"Transformers & LLMs — Tool Use / Function Calling","Letting an LLM invoke external tools or APIs to act, not just talk.","Tool Use (Function Calling)","Turns a text model into an agent that can search, run code or call services.",["llm","agents"],2023),
(3,"Transformers & LLMs — Zero-Shot vs Few-Shot","The difference between giving the model no examples versus a few in the prompt.","Zero-Shot vs Few-Shot","Zero-shot relies purely on instructions; few-shot supplies examples to steer format and behavior.",["llm"],2020),

# ---- L4 ----
(4,"Transformers & LLMs — Why Transformers Beat RNNs","The two advantages that let transformers replace recurrent nets for sequences.","Parallelism + Direct Long-Range Links","Self-attention processes all tokens at once and connects distant positions in one hop, fixing RNN slowness and forgetting.",["transformers","theory"],2017),
(4,"Transformers & LLMs — Chinchilla Scaling","The 2022 result that most large models were undertrained on data.","Chinchilla (Compute-Optimal Scaling)","Hoffmann et al. showed data and parameters should scale together; a smaller model on more tokens beat larger ones.",["llm","theory"],2022),
(4,"Transformers & LLMs — InstructGPT","The 2022 work that applied RLHF to make GPT-3 follow instructions and align with intent.","InstructGPT","Showed a smaller aligned model could be preferred over raw GPT-3 — the recipe behind ChatGPT.",["llm","alignment"],2022),
(4,"Transformers & LLMs — HHH Framework","Anthropic's three guiding properties for aligned assistants.","Helpful, Harmless, Honest","The HHH triad frames the alignment target that Constitutional AI and RLHF optimize toward.",["claude","alignment"],2021),
(4,"Transformers & LLMs — Claude Code","Anthropic's agentic coding tool that works directly in the developer's environment.","Claude Code","An LLM agent that reads, edits and runs code via the terminal, turning Claude into a hands-on coding collaborator.",["claude","agents","product"],2025),
(4,"Transformers & LLMs — Model Context Protocol","Anthropic's open standard for connecting LLMs to external tools and data.","Model Context Protocol (MCP)","Introduced in 2024; a universal interface so agents can plug into many data sources and services.",["claude","agents"],2024),
(4,"Transformers & LLMs — Causal vs Masked Attention","Why GPT can't peek ahead while BERT can see the whole sentence.","Causal Masking","Decoder models mask future tokens so each position only attends to the past, enabling left-to-right generation.",["transformers","theory"],2018),
(4,"Transformers & LLMs — Claude Model Tiers","Anthropic's naming pattern spanning the largest to the fastest Claude models.","Opus / Sonnet / Haiku","The family trades capability for speed/cost — Opus most capable, Haiku fastest — so users pick per task.",["claude"],2024),
(4,"Transformers & LLMs — Why GPT-3 Surprised Researchers","The capability that emerged from sheer scale without task-specific training.","Few-Shot In-Context Learning","At 175B parameters the model could perform new tasks from prompt examples alone, hinting that scale unlocks generality.",["llm","theory"],2020),

# ---- L5 ----
(5,"Transformers & LLMs — Transformer Block Anatomy","The repeating sub-layers that make up a single transformer layer.","Attention + FFN + Residual/LayerNorm","Each block = multi-head self-attention then a feed-forward net, each wrapped with residual connections and layer normalization.",["transformers","theory"],2017),
(5,"Transformers & LLMs — Kaplan vs Chinchilla","The shift in scaling guidance between the 2020 and 2022 results.","Parameters-First vs Data-Balanced","Kaplan emphasized parameter scaling; Chinchilla corrected it, showing tokens should grow about proportionally with parameters.",["llm","theory"],2022),
(5,"Transformers & LLMs — RLHF Mechanics","The two-model loop that turns human rankings into a training signal.","Reward Model + PPO","A reward model learns from human preference rankings, then PPO fine-tunes the LLM to maximize that reward.",["llm","alignment"],2022),
(5,"Transformers & LLMs — RLAIF","Replacing human feedback with AI-generated feedback guided by principles.","RLAIF (Constitutional AI)","Anthropic's approach uses model self-critique against a constitution, scaling alignment with less human labeling.",["claude","alignment"],2022),
(5,"Transformers & LLMs — Mixture of Experts","A sparse design where each token is routed to only a few expert sub-networks.","Mixture of Experts (MoE)","Boosts parameter count without proportional compute by activating a subset of experts per token.",["transformers","theory"],2021),
(5,"Transformers & LLMs — KV Cache","The inference optimization that stores past keys and values to avoid recomputation.","Key–Value Cache","Lets autoregressive generation reuse prior attention computation, making token-by-token decoding efficient.",["transformers","inference"],2020),
(5,"Transformers & LLMs — Chain-of-Thought","Prompting a model to reason step by step before answering.","Chain-of-Thought Prompting","Wei et al. (2022); eliciting intermediate steps sharply improves multi-step reasoning in large models.",["llm","reasoning"],2022),
(5,"Transformers & LLMs — ReAct Agent Loop","The pattern interleaving reasoning with tool actions and observations.","ReAct","Yao et al. (2022); 'reason + act' cycles let an LLM plan, call tools, observe results and iterate — the basis of coding agents.",["agents","reasoning"],2022),
(5,"Transformers & LLMs — Agentic Loop","The general cycle by which a tool-using LLM pursues a goal over many steps.","Perceive–Plan–Act–Observe","Modern agents (incl. Claude Code) repeatedly read state, decide an action, execute a tool, and incorporate feedback until done.",["agents"],2024),
],
}

def slug(s):
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s[:40]

SHORT = {"foundations":"fnd","vision_sequence":"vsq","representations":"rep","transformers_llms":"llm"}

def main():
    cards = []
    seen = set()
    for cat in CATEGORIES:
        cid = cat["id"]
        for i, (diff, headline, a, b, notes, tags, year) in enumerate(DECK[cid], 1):
            cid_short = SHORT[cid]
            base = f"{cid_short}-{i:02d}-{slug(b)}"
            uid = base
            n = 2
            while uid in seen:
                uid = f"{base}-{n}"; n += 1
            seen.add(uid)
            cards.append({
                "id": uid, "category": cid, "difficulty": diff,
                "concept": headline, "a": [a], "b": [b], "notes": notes,
                "tags": tags, "year": year,
            })

    lines = ["["]
    for k, c in enumerate(cards):
        comma = "," if k < len(cards) - 1 else ""
        lines.append("  " + json.dumps(c, ensure_ascii=False, separators=(",", ":")) + comma)
    lines.append("]")
    out = "\n".join(lines) + "\n"
    with open("ml_flashcards/cards.json", "w", encoding="utf-8") as f:
        f.write(out)

    from collections import Counter
    print(f"TOTAL CARDS: {len(cards)}")
    for cat in CATEGORIES:
        cc = [c for c in cards if c["category"] == cat["id"]]
        tiers = Counter(c["difficulty"] for c in cc)
        print(f"  {cat['id']:18s} {len(cc):3d}  tiers L1-L5: " +
              " ".join(f"{tiers.get(t,0)}" for t in range(1, 6)))

if __name__ == "__main__":
    main()
