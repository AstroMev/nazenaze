import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    SystemMessage,
    HumanMessage,
    AIMessage
)
from langchain.callbacks import get_openai_callback


def init_page():
    st.set_page_config(
        page_title="なぁぜなぁぜGPT 🤗",
        page_icon="🤗"
    )
    st.header("なぁぜなぁぜGPT 🤗")
    st.sidebar.title("Options")


def init_messages():
    clear_button = st.sidebar.button("Clear Conversation", key="clear")
    if clear_button or "messages" not in st.session_state:
        st.session_state.messages = [
            SystemMessage(content="You are a helpful assistant.")
        ]
        st.session_state.costs = []


def select_model():
    model = st.sidebar.radio("Choose a model:", ("GPT-3.5", "GPT-4"))
    if model == "GPT-3.5":
        model_name = "gpt-3.5-turbo"
    else:
        model_name = "gpt-4"

    # Add a slider to allow users to select the temperature from 0 to 2.
    # The initial value should be 0.0, with an increment of 0.01.
    temperature = st.sidebar.slider("Temperature:", min_value=0.0, max_value=2.0, value=0.0, step=0.01)

    return ChatOpenAI(temperature=temperature, model_name=model_name)


def get_answer(llm, messages):
    with get_openai_callback() as cb:
        answer = llm(messages)
    return answer.content, cb.total_cost


def main():
    init_page()

    llm = select_model()
    init_messages()

    nazenaze_prompt = """
なぜなぜ分析アプリへようこそ！
このアプリケーションでは、発生した事象に対して5回「なぜ？」を深堀りすることで問題の根本を発見し、その対策を練ることができます。

まずはじめに、ユーザーから発生事象を聞き出します。
ユーザーの入力を[発生事象]に保存してください。
その後、[分析]コマンドを実行してください。

##
[分析]
・{count}が5以下のとき
あなたの目的は、[発生事象]の根本原因を突き止めることです。
この目的を達成するために、あなたは毎回の応答でユーザーに{count}-1で入力された内容についてそれが発生した原因を追求するための質問をします。

・{count}が6以上のとき
ユーザーに対して「以上を踏まえて、今後の対策案はありますか？」と質問します。
ユーザーの入力を[対策]として保存します。
[対策]が入力されたら、それまでの会話を元にサマリーを出力してください。
サマリーはMarkdown形式で、報告書として出力してください。

##
あなたの応答回数をカウントする変数{count}を用意し、応答時には{count}をインクリメントしてください。
応答するときは，文章の最後に，「（今は{count}回目の応答です）」と加えてください。
{count}は0からスタートします。

##
こんにちは
user:
}
"""

    # Monitor user input
    if user_input := st.chat_input("何がありましたか？:"):
        st.session_state.messages.append(HumanMessage(content=user_input))
        with st.spinner("ChatGPT is typing ..."):
            answer, cost = get_answer(llm, st.session_state.messages)
        st.session_state.messages.append(AIMessage(content=answer))
        st.session_state.costs.append(cost)

    messages = st.session_state.get('messages', [])
    for message in messages:
        if isinstance(message, AIMessage):
            with st.chat_message('assistant'):
                st.markdown(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message('user'):
                st.markdown(message.content)
        else:  # isinstance(message, SystemMessage):
            st.write(f"失敗は成功のもと！一緒に反省して次へ進みましょう！")

    costs = st.session_state.get('costs', [])
    st.sidebar.markdown("## Costs")
    st.sidebar.markdown(f"**Total cost: ${sum(costs):.5f}**")
    for cost in costs:
        st.sidebar.markdown(f"- ${cost:.5f}")

if __name__ == '__main__':
    main()
