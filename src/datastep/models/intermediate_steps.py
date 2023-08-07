import dataclasses


@dataclasses.dataclass
class IntermediateSteps:
    input: str | None
    top_k: int | None
    dialect: str | None
    table_info: str | None
    sql_query: str | None
    sql_result: list[dict] | None
    verbose_result: str | None

    @classmethod
    def from_chain_steps(cls, steps: list):
        if steps:
            desc = steps[0] if len(steps) > 0 else {}
            sql_query = steps[1] if len(steps) > 1 else None
            sql_result = steps[3] if len(steps) > 3 else None
            verbose_result = steps[5] if len(steps) > 5 else None
            return cls(
                input=desc.get("input"),
                top_k=desc.get("top_k"),
                dialect=desc.get("dialect"),
                table_info=desc.get("table_info"),
                sql_query=sql_query,
                sql_result=sql_result,
                verbose_result=verbose_result,
            )
        return None
