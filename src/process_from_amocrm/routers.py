"""amoCRM chats router."""

from fastapi import APIRouter, Request, Response, status

amocrm_router = APIRouter(
    tags=["amoCRM"],
)


@amocrm_router.post(
    "/location/{scope_id}",
    description="Processing message from amoCRM chats.",
)
async def amocrm_handler(scope_id: str, request: Request):
    json_body = await request.json()

    chat_id = json_body["message"]["conversation"]["client_id"]
    message = json_body["message"]["message"]["text"]

    # any message processing

    return Response(status_code=status.HTTP_200_OK)
