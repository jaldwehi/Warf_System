from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.db.models import Q
import re
from records.models import KnowledgeChunk


@login_required
def chat_view(request):
    return render(request, "assistant/chat.html")



def retrieve_chunks(query: str, k: int = 5):
    qtext = (query or "").lower()
    # كلمات شائعة نرميها
    stop = {"what","is","the","a","an","please","tell","me","about","give","show","for","of","to","in","on","and","with","?"}
    words = re.findall(r"[a-zA-Z0-9_]+", qtext)
    keywords = [w for w in words if w not in stop]

    # لو ما طلع keywords، نستخدم النص كامل
    if not keywords:
        keywords = [qtext.strip()] if qtext.strip() else []

    # Q OR على كل كلمة
    q_obj = Q()
    for kw in keywords[:6]:  # حد بسيط
        q_obj |= Q(text__icontains=kw) | Q(document__title__icontains=kw) | Q(document__content__icontains=kw)

    # تحسين إضافي: لو السؤال عن decision نبحث عن DECISION: مباشرة
    if "decision" in keywords:
        q_obj |= Q(text__icontains="DECISION:") | Q(document__content__icontains="DECISION:")

    qs = KnowledgeChunk.objects.select_related("document").filter(q_obj).order_by("-created_at")[:k]

    results = []
    for ch in qs:
        results.append({
            "title": ch.document.title,
            "doc_type": ch.document.doc_type,
            "meeting_id": ch.document.external_meeting_id,
            "snippet": ch.text[:650],
        })
    return results


@login_required
@require_POST
def ask_api(request):
    question = (request.POST.get("question") or "").strip()
    if not question:
        return JsonResponse({"ok": False, "error": "Empty question"}, status=400)

    sources = retrieve_chunks(question, k=5)

    if not sources:
       return JsonResponse({
        "ok": True,
        "answer": "I couldn't find a clear match in the current knowledge base. Try different keywords (e.g., decision, problem, tasks) or rephrase your question.",
        "sources": []
})


   # Initial answer (RAG without LLM)
    answer_lines = ["I found relevant information in the WARF Knowledge Base:\n"]

    for i, s in enumerate(sources, start=1):
       answer_lines.append(
        f"{i}) {s['title']} — ({s['doc_type']}) meeting: {s['meeting_id']}"
    )

    answer_lines.append("\nYou can review the related sources below.")

    return JsonResponse({
        "ok": True,
        "answer": "\n".join(answer_lines),
        "sources": sources
    })
