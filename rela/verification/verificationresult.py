from dataclasses import dataclass

@dataclass
class VerificationResult:
    data: str
    spec: str
    n_total: int
    n_passed: int
    n_failed: int
    n_skipped: int
    passed_cases: list
    failed_cases: list
    skipped_cases: list

    def __bool__(self):
        return self.n_failed == 0 and self.n_passed > 0
    
    def is_passed(self):
        return self.__bool__()

    def __str__(self):
        return f'{self.n_passed}/{self.n_total} cases passed'
    
