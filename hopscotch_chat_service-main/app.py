"""Simple local teaching example. Run: uvicorn app:app --port 8001"""
from fastapi import FastAPI, Header, HTTPException
from langchain_core.messages import HumanMessage, AIMessage
import httpx
from session_tools import API_URL
from shop_chain import chain
from redis_memory import save_message, load_history

app = FastAPI()

# One conversation per login token, kept in this backend process.
chat_history = {}


# @app.post("/chat")
# def chat(user_input: dict, authorization: str = Header()):
#     # Streamlit sends: Authorization: Bearer <shopping login token>
#     # This is the token Streamlit received when you signed in.
#     login_token = authorization.removeprefix("Bearer ")

#     # For this demo, use the login token as the user's history ID.

#     # Here email address is used to get user_id, you should ideally use a token to get user_id from redis
#     user = httpx.get(f'{API_URL}/me',
#                     headers={'Authorization': authorization}, timeout=30)

#     if user.status_code != 200:
#         return HTTPException(401, 'Please sign in again.')
#     user.raise_for_status()

#     user_id = user.json()['customer_id']

#     history = load_history(user_id)

#     # Send the question, history, and login token to our chain.
#     response = chain.invoke(
#         {"query": user_input["query"], "history": history.messages},
#         config={"configurable": {"user_id": user_id, "login_token": login_token}},
#     )

#     # # Save the question and answer for the next request.
#     # history.append(HumanMessage(content=user_input["query"]))
#     # history.append(AIMessage(content=response.content))

#     save_message(user_id, HumanMessage(content=user_input['query']))
#     save_message(user_id, response)

#     return {"answer": response.content}



@app.post('/chat')
def chat(user_input: dict, authorization: str = Header()):
    stage = "checking login"

    try:
        login_token = authorization.removeprefix('Bearer ')

        user = httpx.get(
            f'{API_URL}/me',
            headers={'Authorization': authorization},
            timeout=30,
        )
        if user.status_code == 401:
            raise HTTPException(401, 'Please sign in again.')

        user.raise_for_status()
        user_id = user.json()['customer_id']

        stage = "loading Redis history"
        history = load_history(user_id)

        stage = "calling the chain"
        response = chain.invoke(
            {'query': user_input['query'], 'history': history.messages},
            config={'configurable': {
                'user_id': user_id,
                'login_token': login_token,
            }},
        )

        stage = "saving Redis messages"
        save_message(user_id, HumanMessage(content=user_input['query']))
        save_message(user_id, response)

        return {'answer': response.content}

    except HTTPException:
        raise
    except Exception as error:
        import traceback
        traceback.print_exc()
        return {'answer': f'Failed while {stage}: {type(error).__name__}'}