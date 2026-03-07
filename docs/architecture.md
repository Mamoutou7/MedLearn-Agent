.
├── docs
│   └── architecture.md
├── README.md
├── requirements.txt
├── scripts
│   └── run_healthbot.py
├── src
│   └── healthbot
│       ├── __init__.py
│       ├── cli
│       │   └── run.py
│       ├── config
│       │   ├── __init__.py
│       │   └── settings.py
│       ├── graph
│       │   ├── __init__.py
│       │   └── workflow.py
│       ├── llm
│       │   ├── __init__.py
│       │   └── llm_provider.py
│       ├── models
│       │   ├── __init__.py
│       │   ├── quiz_models.py
│       │   └── state.py
│       ├── nodes
│       │   ├── __init__.py
│       │   ├── agent.py
│       │   ├── entry.py
│       │   ├── quiz_nodes.py
│       │   ├── rejection.py
│       │   └── validation.py
│       ├── routers
│       │   ├── __init__.py
│       │   └── workflow_router.py
│       ├── tools
│       │   ├── __init__.py
│       │   └── med_web_search.py
│       └── utils
│           ├── __init__.py
│           ├── interrupts.py
│           └── visualization.py
└── tests
    ├── test_quiz.py
    ├── test_validation.py
    └── test_workflow.py

15 directories, 31 files
