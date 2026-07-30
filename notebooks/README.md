# intro-path-planning

**still under construction** and License will most likely change to MIT or something similar...


# Robot Path Planning: PRM Implementations and Benchmarking

This repository contains our extended implementation and evaluation of robotic path planning algorithms. The relevant file is notebooks/Abgabe.ipynb

## Project Structure and Modifications

Compared to the original upstream repository, we have extended the architecture and modified several core components to integrate our solutions.

### Newly Added Files
These files were created from scratch to introduce new algorithms, visualizations, and documentation:

**Core Implementations & Architecture:**
*   `notebooks/AbstractGraphPRM.py`: Base class providing shared graph functionalities for our PRM implementations.
*   `notebooks/IPEarlyPRM.py`: Our custom implementation of the EarlyPRM algorithm.
*   `notebooks/IPNodeSampling.py`: Contains custom sampling strategies.
*   `notebooks/diagrams/architecture.puml` & `architecture.png`: UML diagrams visualizing our software architecture.

**Benchmarking & Visualization:**
*   `notebooks/IPPlanarManipulatorBenchmarks.py`: New benchmark scenarios specifically designed to test narrow passages and complex environments.
*   `notebooks/IPSamplerVisualizer.py`: Tooling to visually evaluate the distribution and validity of sampled nodes.

**Results & Deliverables:**
*   `notebooks/Abgabe.ipynb`: Our main submission notebook containing the guided execution and explanation of our results.
*   `notebooks/task8_benchmark_results.csv`: Exported data from our benchmark runs.
*   `notebooks/task10_lazy_sensitivity.csv`: Data evaluating the parameter sensitivity of the LazyPRM.
*   `notebooks/task10_planner_comparison.csv`: Direct performance comparison metrics between LazyPRM and EarlyPRM.

### Modified Files
We adapted the following existing modules to fix bugs, integrate our new algorithms, and expand the test suites:

*   **Algorithms & Logic:** `notebooks/IPLazyPRM.py`, `notebooks/IPEnvironmentKin.py`, `notebooks/IPPlanarManipulator.py`
*   **Testing & Visualization:** `notebooks/IPTestSuite.py`, `notebooks/IPVISLazyPRM.py`
*   **Notebooks:** `notebooks/IP-7-0-PRM-Lazy.ipynb`, `notebooks/IP-X-1-Automated_PlanerTest.ipynb`
*   **Configuration:** `.gitignore`

---

## AI Usage Disclosure

During the development of this project, we utilized Large Language Models (specifically **ChatGPT**, **Claude**, and **Gemini**) as interactive development assistants. In accordance with the course guidelines, our use of these tools is documented below:

**1. Purpose of AI usage:**
We primarily used AI tools to accelerate our workflow when familiarizing ourselves with new Python libraries. Additionally, we utilized them as a sounding board for debugging error messages and to help draft, structure, and refine our code documentation and English texts for better readability.

**2. Accepted suggestions:**
We incorporated AI-generated explanations regarding API functionalities especially for visualizations. We also integrated isolated code snippets for bug fixes and accepted suggestions for code refactoring and linguistic improvements in our documentation.

**3. Rejected suggestions:**
We strictly rejected any code suggestions that were faulty or simply did not fit into our overall concept and the existing architecture. Regarding text generation, we frequently rejected or heavily edited AI suggestions, as the models tended to exaggerate or use unnatural phrasing.

**4. Verification of functionality:**
The core ideas and conceptual designs for the implemented algorithms were exclusively our own. No AI-generated code was blindly copy-pasted into the final submission. To trace and evaluate the algorithms effectively, we developed additional custom tools that operate primarily on a visual basis (e.g., `IPSamplerVisualizer.py`). Because these tools allow us to visually track the algorithms' behavior step-by-step, we could very quickly spot any inconsistencies or errors. Every accepted snippet was manually integrated, analyzed, and thoroughly validated thoroughly.

Eric Schubert & Philipp Meyer