from dto.instruction_dto import InstructionDto
# from infra.supabase import supabase


def get_instruction_by_tenant_id(tenant_id: int) -> InstructionDto:
    pass
    # response = supabase.table("tenant").select("*").eq("id", tenant_id).execute()
    #
    # instruction_id = response.data[0]["instruction_id"]
    # response = supabase.table("instruction").select("*").eq("id", instruction_id).execute()
    #
    # return InstructionDto(**response.data[0])
