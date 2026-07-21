"""MySQL 数据库连接管理，提供连接池和安全的查询封装。"""

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from config import config


class DatabaseManager:
    """MySQL 数据库管理器，封装连接池和只读查询。"""

    def __init__(self):
        self._engine: Engine = create_engine(
            config.mysql_url(),
            pool_size=5,
            pool_recycle=3600,
            echo=False,
        )

    @property
    def engine(self) -> Engine:
        return self._engine

    def test_connection(self) -> bool:
        """测试数据库连接是否正常。"""
        try:
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            print(f"[DB] 连接失败: {e}")
            return False

    def execute_query(self, sql: str, params: dict | None = None) -> list[dict]:
        """执行只读 SELECT 查询，返回字典列表。

        安全限制：仅允许以 SELECT/SHOW/DESCRIBE 开头的语句。
        """
        sql_stripped = sql.strip().upper()
        if not (
            sql_stripped.startswith("SELECT")
            or sql_stripped.startswith("SHOW")
            or sql_stripped.startswith("DESCRIBE")
        ):
            raise ValueError(f"仅允许只读查询，拒绝执行: {sql[:50]}")

        with self._engine.connect() as conn:
            result = conn.execute(text(sql), params or {})
            rows = result.mappings().all()
            return [dict(row) for row in rows]


# 全局单例
db_manager = DatabaseManager()
