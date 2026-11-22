import json
import string
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parents[1] / "eval"


def single_choice_score(prediction, answer, position):
    letters = [char for char in prediction if char in string.ascii_letters]
    index = 0 if position == "start" else -1
    return int(bool(letters) and letters[index].upper() == answer)


class ReferenceScoringTests(unittest.TestCase):
    def check_scoring(self, questions, references, scores, improvement, position="start"):
        predictions = {}
        labels = {}
        expected_scores = {}
        expected_details = {}
        for problem_id, (kind, answer, prediction) in questions.items():
            question_id = f"{problem_id}_0"
            predictions[question_id] = {
                "question_id": question_id,
                "prediction": prediction,
                "question_image_number": 0,
            }
            labels[problem_id] = {
                "problem_answer_list": [answer],
                "problem_type_list": [kind],
                "problem_analysis_list": ["合成测试"],
                "subject": ["数学"],
                "education": "初中",
            }
        for problem_id in sorted(questions):
            question_id = f"{problem_id}_0"
            kind, answer, _ = questions[problem_id]
            score, total = scores[problem_id]
            expected_scores[question_id] = {
                "question_id": question_id,
                "score": score,
                "total_score": total,
            }
            expected_details[question_id] = {
                **predictions[question_id],
                **expected_scores[question_id],
                "analysis": "合成测试",
                "answer": answer,
                "type": kind,
                "education": "初中",
                "subject": "数学",
            }

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            inputs = {root / "prediction.json": predictions, root / "labels.json": labels}
            command = [
                sys.executable, "-X", "utf8", "-B", "metrics.py",
                "--prediction_file", str(root / "prediction.json"),
                "--label_file", str(root / "labels.json"),
                "--answer_position", position,
            ]
            if references is not None:
                ref_path = root / "reference.json"
                inputs[ref_path] = {
                    f"{key}_0": {"prediction": value} for key, value in references.items()
                }
                command.extend(["--reference_file", str(ref_path)])
            for path, records in inputs.items():
                path.write_text(json.dumps(records, ensure_ascii=False), encoding="utf-8")
            original_inputs = {path: path.read_bytes() for path in inputs}

            result = subprocess.run(
                command, cwd=EVAL_DIR, capture_output=True, encoding="utf-8",
                check=False, timeout=30,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual({path: path.read_bytes() for path in inputs}, original_inputs)
            for filename, expected in (
                ("score.json", expected_scores), ("detail.json", expected_details)
            ):
                actual = json.loads((root / filename).read_text(encoding="utf-8"))
                self.assertEqual(actual, expected)
                self.assertEqual(list(actual), list(expected))

        total_score = sum(total for _, total in scores.values())
        absolute_score = sum(score for score, _ in scores.values())
        self.assertIn(
            f"Absolute Score: {absolute_score:.2f}/{total_score}, "
            f"{absolute_score / total_score * 100:.2f}%",
            result.stdout,
        )
        if improvement:
            self.assertIn(
                f"Improvement Score: {improvement:.2f}/{total_score}, "
                f"{improvement / total_score * 100:.2f}%",
                result.stdout,
            )
        else:
            self.assertNotIn("Improvement Score:", result.stdout)

    def test_without_reference_file(self):
        self.check_scoring({"p": ("单选", "A", "B")}, None, {"p": (0, 1)}, 0)

    def test_empty_reference_is_skipped(self):
        self.check_scoring({"p": ("单选", "A", "B")}, {"p": ""}, {"p": (0, 1)}, 0)

    def test_unrelated_reference_is_skipped(self):
        self.check_scoring({"p": ("单选", "A", "B")}, {"other": "A"}, {"p": (0, 1)}, 0)

    def test_single_choice_improvement_requires_a_better_reference(self):
        for prediction, reference in [("B", "(A)."), ("A", "A"), ("A", "B"), ("B", "B")]:
            with self.subTest(prediction=prediction, reference=reference):
                primary = single_choice_score(prediction, "A", "start")
                comparison = single_choice_score(reference, "A", "start")
                self.check_scoring(
                    {"p": ("单选", "A", prediction)},
                    {"p": reference},
                    {"p": (primary, 1)},
                    max(comparison - primary, 0),
                )

    def test_answer_position_applies_to_predictions_and_references(self):
        questions = {"b": ("单选", "A", "A B"), "a": ("单选", "A", "B A")}
        references = {"b": "答案是 B A", "a": "答案是 B"}
        for position in ("start", "end"):
            with self.subTest(position=position):
                scores = {
                    key: (single_choice_score(prediction, answer, position), 1)
                    for key, (_, answer, prediction) in questions.items()
                }
                improvement = sum(
                    max(single_choice_score(references[key], answer, position) - scores[key][0], 0)
                    for key, (_, answer, _) in questions.items()
                )
                self.check_scoring(questions, references, scores, improvement, position)

    def test_multiple_choice_keeps_partial_credit_and_sums_improvements(self):
        self.check_scoring(
            {"b": ("多选", "AB", "B"), "a": ("多选", "AB", "A"), "c": ("多选", "AB", "AB")},
            {"a": "A, A, B", "b": "A B", "c": "B C", "other": "A"},
            {"a": (1, 2), "b": (1, 2), "c": (2, 2)},
            2,
        )

    def test_fill_in_the_blank_scores_alternative_answers(self):
        self.check_scoring(
            {"p": ("填空", "甲或乙\n7", "乙\n0")}, {"p": "甲；7"}, {"p": (1, 2)}, 1
        )

    def test_open_ended_reference_uses_rouge(self):
        self.check_scoring({"p": ("解答", "甲", "乙")}, {"p": "甲"}, {"p": (0, 1)}, 1)


if __name__ == "__main__":
    unittest.main()
