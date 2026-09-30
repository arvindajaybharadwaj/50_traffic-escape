import json
from pathlib import Path


class HighScores:
    def __init__(self, path=None):
        self.path=Path(path) if path is not None else Path(__file__).resolve().parent.parent/"high_scores.json"
        try:
            saved=json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            saved=[]
        if not isinstance(saved,list):
            saved=[]
        self.scores=sorted((score for score in saved if type(score) is int and score>=0),reverse=True)[:5]

    def add(self, score):
        self.scores=sorted((*self.scores,score),reverse=True)[:5]
        temporary=self.path.with_name(self.path.name+".tmp")
        temporary.write_text(json.dumps(self.scores,indent=2)+"\n",encoding="utf-8")
        temporary.replace(self.path)
