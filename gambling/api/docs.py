from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

game_list_docs = swagger_auto_schema(
    operation_description="List all gambling games",
    manual_parameters=[
        openapi.Parameter(
            'status',
            openapi.IN_QUERY,
            description="Filter by game status",
            type=openapi.TYPE_STRING,
            enum=['active', 'completed', 'cancelled']
        ),
        openapi.Parameter(
            'game_type',
            openapi.IN_QUERY,
            description="Filter by game type",
            type=openapi.TYPE_STRING,
            enum=['dice', 'coin', 'roulette']
        )
    ]
)

place_bet_docs = swagger_auto_schema(
    operation_description="Place a bet on a game",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['amount', 'bet_data'],
        properties={
            'amount': openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Bet amount (decimal string)"
            ),
            'bet_data': openapi.Schema(
                type=openapi.TYPE_OBJECT,
                description="Game-specific bet data"
            )
        }
    ),
    responses={
        201: "Bet placed successfully",
        400: "Invalid request (insufficient funds, invalid bet data, etc.)",
        404: "Game not found"
    }
)

game_stats_docs = swagger_auto_schema(
    operation_description="Get game statistics",
    responses={
        200: openapi.Response(
            description="Game statistics",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'total_bets': openapi.Schema(
                        type=openapi.TYPE_INTEGER
                    ),
                    'unique_players': openapi.Schema(
                        type=openapi.TYPE_INTEGER
                    ),
                    'average_bet': openapi.Schema(
                        type=openapi.TYPE_STRING
                    ),
                    'total_pool': openapi.Schema(
                        type=openapi.TYPE_STRING
                    ),
                    'total_fees': openapi.Schema(
                        type=openapi.TYPE_STRING
                    )
                }
            )
        )
    }
)

bet_list_docs = swagger_auto_schema(
    operation_description="List user's bets",
    responses={
        200: "List of user's bets"
    }
)

active_bets_docs = swagger_auto_schema(
    operation_description="List user's active bets",
    responses={
        200: "List of user's active bets"
    }
)

completed_bets_docs = swagger_auto_schema(
    operation_description="List user's completed bets",
    responses={
        200: "List of user's completed bets"
    }
)