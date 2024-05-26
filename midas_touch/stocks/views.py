from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from stocks.helper import get_chat_completion, get_company_fundamentals, get_company_prices, get_company_news_summary, get_company_investment_recommendation, generate_company_knowledge_base
from stocks.models import Stock

class StockViewSet(ViewSet):
    def get_queryset(self):
        return Stock.objects.all()

    @action(detail=False, methods=['post'])
    def insights(self, request):
        prompt = request.data.get('prompt')
        answer = get_chat_completion(prompt)
        return Response({"answer": answer})

    @action(detail=False, methods=['post'])
    def company_fundamentals(self, request):
        ticker = request.data.get('ticker')
        financials, balance_sheet, cash_flow = get_company_fundamentals(ticker)
        data = {
            "financials": financials.to_dict(),
            "balance_sheet": balance_sheet.to_dict(),
            "cash_flow": cash_flow.to_dict(),
        }
        return Response(data)

    @action(detail=False, methods=['post'])
    def company_prices(self, request):
        ticker = request.data.get('ticker')
        timestamps, prices = get_company_prices(ticker)
        return Response({"timestamps": timestamps, "prices": prices})

    @action(detail=False, methods=['post'])
    def company_news_summary(self, request):
        ticker = request.data.get('ticker')
        news_summary = get_company_news_summary(ticker)
        return Response({"news_summary": news_summary})

    @action(detail=False, methods=['post'])
    def company_investment_recommendation(self, request):
        ticker = request.data.get('ticker')
        recommendation = get_company_investment_recommendation(ticker)
        return Response({"recommendation": recommendation})

    @action(detail=False, methods=['post'])
    def knowledge_base(self, request):
        ticker = request.data.get('ticker')
        prompt = request.data.get('prompt')
        knowledge_base = generate_company_knowledge_base(ticker, prompt)
        return Response({"knowledge_base": knowledge_base})
