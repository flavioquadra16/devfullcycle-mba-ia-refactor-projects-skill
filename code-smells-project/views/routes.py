from controllers import pedido_controller
from controllers import produto_controller
from controllers import sistema_controller
from controllers import usuario_controller


def register_routes(app):
    app.add_url_rule("/produtos", view_func=produto_controller.listar_produtos, methods=["GET"])
    app.add_url_rule("/produtos/busca", view_func=produto_controller.buscar_produtos, methods=["GET"])
    app.add_url_rule("/produtos/<int:id>", view_func=produto_controller.buscar_produto, methods=["GET"])
    app.add_url_rule("/produtos", view_func=produto_controller.criar_produto, methods=["POST"])
    app.add_url_rule("/produtos/<int:id>", view_func=produto_controller.atualizar_produto, methods=["PUT"])
    app.add_url_rule("/produtos/<int:id>", view_func=produto_controller.deletar_produto, methods=["DELETE"])

    app.add_url_rule("/usuarios", view_func=usuario_controller.listar_usuarios, methods=["GET"])
    app.add_url_rule("/usuarios/<int:id>", view_func=usuario_controller.buscar_usuario, methods=["GET"])
    app.add_url_rule("/usuarios", view_func=usuario_controller.criar_usuario, methods=["POST"])
    app.add_url_rule("/login", view_func=usuario_controller.login, methods=["POST"])

    app.add_url_rule("/pedidos", view_func=pedido_controller.criar_pedido, methods=["POST"])
    app.add_url_rule("/pedidos", view_func=pedido_controller.listar_todos_pedidos, methods=["GET"])
    app.add_url_rule(
        "/pedidos/usuario/<int:usuario_id>",
        view_func=pedido_controller.listar_pedidos_usuario,
        methods=["GET"],
    )
    app.add_url_rule(
        "/pedidos/<int:pedido_id>/status",
        view_func=pedido_controller.atualizar_status_pedido,
        methods=["PUT"],
    )
    app.add_url_rule("/relatorios/vendas", view_func=pedido_controller.relatorio_vendas, methods=["GET"])
    app.add_url_rule("/health", view_func=sistema_controller.health_check, methods=["GET"])
    app.add_url_rule("/", view_func=sistema_controller.index, methods=["GET"])
    app.add_url_rule("/admin/reset-db", view_func=sistema_controller.reset_database, methods=["POST"])
    app.add_url_rule("/admin/query", view_func=sistema_controller.executar_query, methods=["POST"])
