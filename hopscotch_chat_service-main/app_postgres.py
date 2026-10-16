"""Chat API using PostgreSQL memory. Run: uvicorn app_postgres:app --port 8003"""
import httpx
from fastapi import FastAPI, Header, HTTPException
from langchain_core.messages import HumanMessage

from session_tools import API_URL
from shop_chain import chain
from postgres_memory import save_message, load_history

app = FastAPI(title='Hopscotch PostgreSQL Chat API')


@app.post('/chat')
def chat(user_input: dict, authorization: str = Header()):
    login_token = authorization.removeprefix('Bearer ')

    # Ask the shopping API who is signed in; never take user_id from chat.
    user = httpx.get(f'{API_URL}/me',
                    headers={'Authorization': authorization}, timeout=30)
    if user.status_code == 401:
        raise HTTPException(401, 'Please sign in again.')
    user.raise_for_status()
    user_id = user.json()['customer_id']

    history = load_history(user_id)
    response = chain.invoke(
        {'query': user_input['query'], 'history': history.messages},
        config={'configurable': {'user_id': user_id, 'login_token': login_token}},
    )

    save_message(user_id, HumanMessage(content=user_input['query']))
    save_message(user_id, response)
    return {'answer': response.content}
