---
created: '2026-07-19T08:24:53+00:00'
evidence:
- stage-04/candidates.jsonl
- stage-04/web_search_result.json
- stage-04/references.bib
- stage-04/search_meta.json
id: literature_collect-rc-20260719-082149-cf6fbc
run_id: rc-20260719-082149-cf6fbc
stage: 04-literature_collect
tags:
- literature_collect
- stage-04
- run-rc-20260
title: 'Stage 04: Literature Collect'
---

# Stage 04: Literature Collect

{"paper_id": "oalex-W2613718673", "title": "Faster R-CNN: Towards Real-Time Object Detection with Region Proposal Networks", "authors": [{"name": "Shaoqing Ren", "affiliation": "Microsoft Research (United Kingdom)"}, {"name": "Kaiming He", "affiliation": "Microsoft Research (United Kingdom)"}, {"name": "Ross Girshick", "affiliation": "Microsoft Research (United Kingdom)"}, {"name": "Jian Sun", "affiliation": "Microsoft Research (United Kingdom)"}], "year": 2015, "abstract": "State-of-the-art object detection networks depend on region proposal algorithms to hypothesize object locations. Advances like SPPnet and Fast R-CNN have reduced the running time of these detection networks, exposing region proposal computation as a bottleneck. In this work, we introduce a Region Proposal Network (RPN) that shares full-image convolutional features with the detection network, thus enabling nearly cost-free region proposals. An RPN is a fully convolutional network that simultaneously predicts object bounds and objectness scores at each position. The RPN is trained end-to-end to generate high-quality region proposals, which are used by Fast R-CNN for detection. We further merge RPN and Fast R-CNN into a single network by sharing their convolutional features---using the recently popular terminology of neural networks with 'attention' mechanisms, the RPN component tells the unified network where to look. For the very deep VGG-16 model, our detection system has a frame rate of 5fps (including all steps) on a GPU, while achieving state-of-the-art object detection accuracy on PASCAL VOC 2007, 2012, and MS COCO datasets with only 300 proposals per image. In ILSVRC and COCO 2015 competitions, Faster R-CNN and RPN are the foundations of the 1st-place winning entries in several tracks. Code has been made publicly available.", "venue": "arXiv (Cornell University)", "citation_count": 18240, "doi": "10.48550/arxiv.1506.01497", "arxiv_id": "", "url": "https://doi.org/10.48550/arxiv.1506.01497", "source": "openalex", "cite_key": "ren2015faster", "collected_at": "2026-07-19T08:24:26+00:00"}
{"paper_id": "oalex-W2981731882", "title": "Explainable Artificial Intelligence (XAI): Concepts, taxonomies, opportunities and challenges toward responsible AI", "authors": [{"name": "Alejandro Barredo Arrieta", "affiliation": "Tecnalia"}, {"name": "Natalia Díaz-Rodríguez", "affiliation": "École Nationale Supérieure de Techniques Avancées"}, {"name": "Javier Del Ser", "affiliation": "Tecnalia"}, {"name": "Adrien Bennetot", "affiliation": "École Nationale Supérieure de Techniques Avancées"}, {"name": "Siham Tabik", "affiliation": "Universidad de Granada"}, {"name": "Alberto Barbado", "affiliation": "Telefónica (Spain)"}, {"name": "Salvador García", "affiliation": "Universidad de Granada"}, {"name": "Sergio Gil-López", "affiliation": "Tecnalia"}, {"name": "Daniel Molina", "affiliation": "Universidad de Granada"}, {"name": "Richard Benjamins", "affiliation": "Telefónica (Spain)"}, {"name": "Raja Chatila", "affiliation": "Sorbonne Université"}, {"name": "Francisco Herrera", "affiliation": "Universidad de Granada"}], "year": 2019, "abstract": "", "venue": "Information Fusion", "citation_count": 9236, "doi": "10.1016/j.inffus.2019.12.012", "arxiv_id": "", "url": "https://doi.org/10.1016/j.inffus.2019.12.012", "source": "openalex", "cite_key": "arrieta2019explainable", "collected_at": "2026-07-19T08:24:26+00:00"}
{"paper_id": "oalex-W3135028703", "title": "Machine Learning: Algorithms, Real-World Applications and Research Directions", "authors": [{"name": "Iqbal H. Sarker", "affiliation": "Chittagong University of Engineering & Technology"}], "year": 2021, "abstract": "", "venue": "SN Computer Science", "citation_count": 5206, "doi": "10.1007/s42979-021-00592-x", "arxiv_id": "", "url": "https://doi.org/10.1007/s42979-021-00592-x", "source": "openalex", "cite_key": "sarker2021machine", "collected_at": "2026-07-19T08:24:26+00:00"}
{"paper_id": "oalex-W1998933811", "title": "Does Gamification Work? -- A Literature Review of Empirical Studies on Gamification", "authors": [{"name": "Juho Hamari", "affiliation": "University Ucinf"}, {"name": "Jonna Koivisto", "affiliation": "University Ucinf"}, {"name": "Harri Sarsa", "affiliation": "Aalto University"}], "year": 2014, "abstract": "This paper reviews peer-reviewed empirical studies on gamification. We create a framework for examining the effects of gamification by drawing from the definitions of gamification and the discussion on motivational affordances. The literature review covers results, independent variables (examined motivational affordances), dependent variables (examined psychological/behavioral outcomes from gamification), the contexts of gamification, and types of studies performed on the gamified systems. The paper examines the state of current research on the topic and points out gaps in existing literature. The review indicates that gamification provides positive effects, however, the effects are grea

... (truncated, see full artifact)


{
  "topic": "NTM-style differentiable expert memory for task-agnostic class-incremental learning with pretrained Vision Transformers: compare latent expert memory, basis memory, hybrid allocate-or-write, and CaRE plus memory routing under matched parameters and compute; use real literature and real experiments only.",
  "web_results_count": 0,
  "scholar_papers_count": 0,
  "crawled_pages_count": 0,
  "pdf_extractions_count": 0,
  "has_search_answer": false,
  "elapsed_seconds": 27.637230813968927,
  "web_results": [],
  "scholar_papers": []
}

@article{ren2015faster,
  title = {Faster R-CNN: Towards Real-Time Object Detection with Region Proposal Networks},
  author = {Shaoqing Ren and Kaiming He and Ross Girshick and Jian Sun},
  year = {2015},
  journal = {arXiv (Cornell University)},
  doi = {10.48550/arxiv.1506.01497},
  url = {https://doi.org/10.48550/arxiv.1506.01497},
}

@article{arrieta2019explainable,
  title = {Explainable Artificial Intelligence (XAI): Concepts, taxonomies, opportunities and challenges toward responsible AI},
  author = {Alejandro Barredo Arrieta and Natalia Díaz-Rodríguez and Javier Del Ser and Adrien Bennetot and Siham Tabik and Alberto Barbado and Salvador García and Sergio Gil-López and Daniel Molina and Richard Benjamins and Raja Chatila and Francisco Herrera},
  year = {2019},
  journal = {Information Fusion},
  doi = {10.1016/j.inffus.2019.12.012},
  url = {https://doi.org/10.1016/j.inffus.2019.12.012},
}

@article{sarker2021machine,
  title = {Machine Learning: Algorithms, Real-World Applications and Research Directions},
  author = {Iqbal H. Sarker},
  year = {2021},
  journal = {SN Computer Science},
  doi = {10.1007/s42979-021-00592-x},
  url = {https://doi.org/10.1007/s42979-021-00592-x},
}

@article{hamari2014gamification,
  title = {Does Gamification Work? -- A Literature Review of Empirical Studies on Gamification},
  author = {Juho Hamari and Jonna Koivisto and Harri Sarsa},
  year = {2014},
  doi = {10.1109/hicss.2014.377},
  url = {https://doi.org/10.1109/hicss.2014.377},
}

@article{butler2018machine,
  title = {Machine learning for molecular and materials science},
  author = {Keith T. Butler and Daniel W. Davies and Hugh Cartwright and Olexandr Isayev and Aron Walsh},
  year = {2018},
  journal = {Nature},
  doi = {10.1038/s41586-018-0337-2},
  url = {https://doi.org/10.1038/s41586-018-0337-2},
}

@article{campos2021orbslam,
  title = {ORB-SLAM3: An Accurate Open-Source Library for Visual, Visual–Inertial, and Multimap SLAM},
  author = {Carlos Campos and Richard Elvira and Juan J. Gomez Rodriguez and Jose M. M. Montiel and Juan D. Tardos},
  year = {2021},
  journal = {IEEE Transactions on Robotics},
  doi = {10.1109/tro.2021.3075644},
  url = {https://doi.org/10.1109/tro.2021.3075644},
}

@article{dai2019transformerxl,
  title = {Transformer-XL: Attentive Language Models beyond a Fixed-Length Context},
  author = {Zihang Dai and Zhilin Yang and Yiming Yang and Jaime Carbonell and Quoc V. Le and Ruslan Salakhutdinov},
  year = {2019},
  doi = {10.18653/v1/p19-1285},
  url = {https://doi.org/10.18653/v1/p19-1285},
}

@article{liu2019deep,
  title = {Deep Learning for Generic Object Detection: A Survey},
  author = {Li Liu and Wanli Ouyang and Xiaogang Wang and Paul Fieguth and Jie Chen and Xinwang Liu and Matti Pietikäinen},
  year = {2019},
  journal = {International Journal of Computer Vision},
  doi = {10.1007/s11263-019-01247-4},
  url = {https://doi.org/10.1007/s11263-019-01247-4},
}

@article{ji2021survey,
  title = {A Survey on Knowledge Graphs: Representation, Acquisition, and Applications},
  author = {Shaoxiong Ji and Shirui Pan and Erik Cambria and Pekka Marttinen and Philip S. Yu},
  year = {2021},
  journal = {IEEE Transactions on Neural Networks and Learning Systems},
  doi = {10.1109/tnnls.2021.3070843},
  url = {https://doi.org/10.1109/tnnls.2021.3070843},
}

@article{chetty2016effects,
  title = {The Effects of Exposure to Better Neighborhoods on Children: New Evidence from the Moving to Opportunity Experiment},
  author = {Raj Chetty and Nathaniel Hendren and Lawrence F. Katz},
  year = {2016},
  journal = {American Economic Review},
  doi = {10.1257/aer.20150572},
  url = {https://doi.org/10.1257/aer.20150572},
}

@article{dell2014learn,
  title = {What Do We Learn from the Weather? The New Climate-Economy Literature},
  author = {Melissa Dell and Benjamin F. Jones and Benjamin Olken},
  year = {2014},
  journal = {Journal of Economic Literature},
  doi = {10.1257/jel.52.3.740},
  url = {https://doi.org/10.1257/jel.52.3.740},
}

@article{laborde2017heart,
  title = {Heart Rate Variability and Cardiac Vagal Tone in Psychophysiological Research – Recommendations for Experiment Planning, Data Analysis, and Data Reporting},
  author = {Sylvain Laborde and Emma Mosley and Julian F. Thayer},
  year = {2017},
  journal = {Frontiers in Psychology},
  doi = {10.3389/fpsyg.2017.00213},
  url = {https://doi.org/10.3389/fpsyg.2017.00213},
}

@article{jones2020characterising,
  title = {Characterising the Digital Twin: A systematic literature review},
  author = {David Jones and Chris Snider and Aydin Nassehi and Jason Yon and Ben Hicks},
  year = {2020},
  journal = {CIRP journal of manufacturing science and technology},
  doi = {10.1016/j.cirpj.2020.02.002},
  url = {https://doi.org/10.1016/j.cirpj.2020.02.002},
}

@article{paxton2018modules,
  title = {Modules for Experiments in Stellar Astrophysics ( ): Convective Boundaries, Element Diffusion, and Massive Star Explosions},
  author = {Bi

... (truncated, see full artifact)


{
  "real_search": true,
  "queries_used": [
    "\"Neural Turing Machines\" Graves Wayne Danihelka",
    "\"Hybrid computing using a neural network with dynamic external memory\"",
    "\"Scaling Continual Learning to 300+ Tasks with Bi-Level Routing Mixture-of-Experts\"",
    "task-agnostic class-incremental learning differentiable memory",
    "class-incremental learning external memory pretrained vision transformer",
    "continual learning mixture of experts dynamic routing adapters",
    "hypernetwork generated adapters continual learning",
    "latent parameter memory neural network hypernetwork",
    "low rank adapter basis composition mixture of adapters",
    "writable key value memory neural network continual learning",
    "\"Learning to Prompt for Continual Learning\" L2P",
    "\"DualPrompt\" continual learning",
    "\"CODA-Prompt\" continual learning",
    "\"Expandable Subspace Ensemble\" EASE class-incremental learning",
    "APER adapter class-incremental learning pretrained models",
    "MOS adapter merging class-incremental learning",
    "TUNA task-specific adapters continual learning",
    "MIN parameter drift continual learning adapter",
    "SEMA self-expansion adapter class-incremental learning",
    "MoAL mixture of adapters continual learning"
  ],
  "year_min": 2014,
  "total_candidates": 571,
  "bibtex_entries": 567,
  "ts": "2026-07-19T08:24:53+00:00"
}