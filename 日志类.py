import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, Union

class LoggerManager:
    """日志管理器类,用于统一配置和管理日志系统

    该类提供了一个统一的日志管理接口,可以配置日志输出格式、存储位置、轮转策略等。
    支持同时输出到文件和控制台,并提供了日志清理等维护功能。

    Attributes:
        log_dir (Path): 日志文件存储目录
        logger (logging.Logger): 日志记录器实例

    Methods:
        __init__: 初始化日志管理器,配置日志参数
        get_logger: 获取日志记录器实例
        set_level: 设置日志级别
        clean_old_logs: 清理过期日志文件
        get_instance: 获取单例日志记录器

    Example:
        >>> logger_manager = LoggerManager()
        >>> logger = logger_manager.get_logger()
        >>> logger.info("这是一条日志消息")
    """
    
    def __init__(self,
                name: str = "app",
                log_dir: Union[str, Path] = "logs", 
                log_level: int = logging.INFO,
                max_bytes: int = 5 * 1024 * 1024,  # 5MB
                backup_count: int = 5,
                log_format: str = '%(asctime)s - %(levelname)s - %(message)s',
                encoding: str = 'utf-8',
                console_output: bool = True):
        """初始化日志管理器

        配置日志记录器的各项参数,包括日志级别、存储位置、轮转策略等。
        可以选择是否同时输出到控制台。

        Args:
            name (str): 日志记录器名称,默认为"app"
            log_dir (Union[str, Path]): 日志文件目录,默认为"logs"
            log_level (int): 日志记录级别,默认为logging.INFO
            max_bytes (int): 单个日志文件最大大小(字节),默认5MB
            backup_count (int): 保留的备份日志文件数量,默认5个
            log_format (str): 日志格式字符串,默认包含时间、级别和消息
            encoding (str): 日志文件编码,默认utf-8
            console_output (bool): 是否同时输出到控制台,默认True

        Raises:
            RuntimeError: 创建日志目录或处理器失败时抛出
        """
        # 保存 name 参数
        self.name = name
        # 保存 log_dir 参数
        self.log_dir = Path(log_dir)
        # 创建目录
        self._set_log_dir()
        self._create_log_dir()
        # 创建日志实例
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        
        # 避免重复添加处理器
        if not self.logger.handlers:
            # 添加文件处理器
            file_handler = self._create_file_handler(
                max_bytes=max_bytes,
                backup_count=backup_count,
                log_format=log_format,
                encoding=encoding
            )
            self.logger.addHandler(file_handler)
            
            # 添加控制台处理器
            if console_output:
                console_handler = self._create_console_handler(log_format)
                self.logger.addHandler(console_handler)
    
    def _set_log_dir(self):
        """设置日志目录为当前脚本所在目录下的子目录
        
        获取当前脚本的绝对路径,然后将日志目录设置在脚本目录下
        """
        # 获取当前脚本的绝对路径
        current_path = os.path.abspath(__file__)
        # 获取脚本所在目录
        script_dir = os.path.dirname(current_path)
        # 设置日志目录为脚本目录下的子目录
        self.log_dir = Path(script_dir) / self.log_dir

    def _create_log_dir(self) -> None:
        """创建日志目录

        创建用于存储日志文件的目录,如果目录已存在则忽略。

        Raises:
            RuntimeError: 创建目录失败时抛出
        """
        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise RuntimeError(f"创建日志目录失败: {e}")
    
    def _create_file_handler(self,
                            max_bytes: int,
                            backup_count: int,
                            log_format: str,
                            encoding: str) -> RotatingFileHandler:
        """创建文件日志处理器

        配置基于文件的日志处理器,支持日志文件轮转。

        Args:
            max_bytes (int): 单个日志文件最大大小(字节)
            backup_count (int): 保留的备份文件数量
            log_format (str): 日志格式字符串
            encoding (str): 日志文件编码

        Returns:
            RotatingFileHandler: 配置好的文件日志处理器

        Raises:
            RuntimeError: 创建处理器失败时抛出
        """
        try:
            log_file = self.log_dir / f"{self.name}_{datetime.now().strftime('%Y%m%d')}.log"
            handler = RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding=encoding
            )
            handler.setFormatter(logging.Formatter(log_format))
            return handler
        except Exception as e:
            raise RuntimeError(f"创建文件处理器失败: {e}")
    
    def _create_console_handler(self, log_format: str) -> logging.StreamHandler:
        """创建控制台日志处理器

        配置输出到控制台的日志处理器。

        Args:
            log_format (str): 日志格式字符串

        Returns:
            logging.StreamHandler: 配置好的控制台日志处理器
        """
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(log_format))
        return handler
    
    def get_logger(self) -> logging.Logger:
        """获取日志记录器实例

        Returns:
            logging.Logger: 配置好的日志记录器实例
        """
        return self.logger
    
    def set_level(self, level: int) -> None:
        """设置日志级别

        Args:
            level (int): 新的日志记录级别
        """
        self.logger.setLevel(level)
    
    def clean_old_logs(self, days: int = 30) -> None:
        """清理指定天数之前的日志文件

        删除修改时间在指定天数之前的所有日志文件。

        Args:
            days (int): 保留的天数,默认30天

        Note:
            清理失败会记录错误日志但不会中断程序运行
        """
        try:
            now = datetime.now()
            for log_file in self.log_dir.glob("*.log*"):
                if (now - datetime.fromtimestamp(log_file.stat().st_mtime)).days > days:
                    log_file.unlink()
        except Exception as e:
            self.logger.error(f"清理旧日志文件失败: {e}")

    @staticmethod
    def get_instance(name: str = "app") -> logging.Logger:
        """获取单例日志记录器

        使用单例模式获取日志记录器实例,确保全局使用同一个记录器。

        Args:
            name (str): 日志记录器名称,默认为"app"

        Returns:
            logging.Logger: 配置好的日志记录器实例
        """
        if not hasattr(LoggerManager, "_instance"):
            LoggerManager._instance = LoggerManager(name=name)
        return LoggerManager._instance.get_logger()

# Example usage
if __name__ == "__main__":
    # 基本使用
    logger_manager = LoggerManager()
    logger = logger_manager.get_logger()
    logger.info("这是一条日志消息")
    
    # 使用不同日志级别
    logger.debug("调试信息")
    logger.info("普通信息")
    logger.warning("警告信息")
    logger.error("错误信息")
    logger.critical("严重错误信息")
    
    # 自定义配置
    custom_logger = LoggerManager(
        name="custom_app",
        log_dir="custom_logs",
        log_level=logging.DEBUG,
        max_bytes=10*1024*1024,  # 10MB
        backup_count=3,
        log_format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 使用单例模式
    logger1 = LoggerManager.get_instance()
    logger2 = LoggerManager.get_instance()
    assert logger1 is logger2  # True
    
    # 记录异常
    try:
        1/0
    except Exception as e:
        logger.error(f"发生错误: {str(e)}", exc_info=True)
    
    # 格式化输出
    user_name = "张三"
    age = 25
    logger.info(f"用户 {user_name} 年龄为 {age}")
    
    # 记录程序运行时间
    import time
    def log_execution_time(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            logger.info(f"函数 {func.__name__} 执行时间: {end_time - start_time:.2f}秒")
            return result
        return wrapper
    
    # 清理旧日志
    logger_manager.clean_old_logs(days=7)  # 清理7天前的日志
    
    # 实际应用场景示例
    # 程序启动记录
    logger.info("程序启动")
    
    # 记录用户操作
    def user_login(username):
        logger.info(f"用户 {username} 登录系统")
    
    # 记录系统状态
    import psutil
    logger.info(f"系统内存使用率: {psutil.virtual_memory().percent}%")
    
    # 记录配置更改
    def update_config(config_name, new_value):
        logger.info(f"更新配置 {config_name}: {new_value}")
    
    # 程序退出记录
    logger.info("程序正常退出")