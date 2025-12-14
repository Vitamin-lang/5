import json
import csv
from datetime import datetime, timedelta
from collections import defaultdict
import matplotlib.pyplot as plt
import pandas as pd
from io import StringIO
import os

class TaskReporting:
    """Модуль отчетности для системы управления задачами"""
    
    def __init__(self, tasks_file="tasks.json"):
        """
        Инициализация модуля отчетности
        
        Args:
            tasks_file: Путь к файлу с задачами
        """
        self.tasks_file = tasks_file
        self.tasks = self._load_tasks()
    
    def _load_tasks(self):
        """Загрузка задач из JSON-файла"""
        if not os.path.exists(self.tasks_file):
            print(f"Файл {self.tasks_file} не найден. Возвращаем пустой список.")
            return []
        
        try:
            with open(self.tasks_file, 'r', encoding='utf-8') as f:
                tasks = json.load(f)
            return tasks
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Ошибка загрузки задач: {e}")
            return []
    
    def _filter_tasks_by_date(self, tasks, period_days=None, start_date=None, end_date=None):
        """
        Фильтрация задач по дате
        
        Args:
            tasks: Список задач
            period_days: Количество дней от текущей даты (например, 7 для недели)
            start_date: Начальная дата (строка в формате YYYY-MM-DD)
            end_date: Конечная дата (строка в формате YYYY-MM-DD)
        
        Returns:
            Отфильтрованный список задач
        """
        filtered_tasks = []
        
        for task in tasks:
            task_date = datetime.fromisoformat(task.get('created_at', '2000-01-01'))
            now = datetime.now()
            
            if period_days:
                # Фильтр по периоду (последние N дней)
                cutoff_date = now - timedelta(days=period_days)
                if task_date >= cutoff_date:
                    filtered_tasks.append(task)
            
            elif start_date and end_date:
                # Фильтр по диапазону дат
                try:
                    start = datetime.fromisoformat(start_date)
                    end = datetime.fromisoformat(end_date)
                    if start <= task_date <= end:
                        filtered_tasks.append(task)
                except ValueError:
                    print("Ошибка формата даты. Используйте YYYY-MM-DD")
        
        return filtered_tasks
    
    def generate_summary_report(self, period="all"):
        """
        Генерация сводного отчета
        
        Args:
            period: Период отчета ("today", "week", "month", "all")
        
        Returns:
            Словарь со статистикой
        """
        if not self.tasks:
            return {"error": "Нет данных для отчета"}
        
        period_map = {
            "today": 1,
            "week": 7,
            "month": 30
        }
        
        if period in period_map:
            filtered_tasks = self._filter_tasks_by_date(self.tasks, period_days=period_map[period])
        else:
            filtered_tasks = self.tasks
        
        # Статистика
        total_tasks = len(filtered_tasks)
        status_count = defaultdict(int)
        completion_rate = 0
        
        for task in filtered_tasks:
            status = task.get('status', 'неизвестно')
            status_count[status] += 1
        
        # Расчет процента завершенных задач
        completed = status_count.get('завершенная', 0)
        if total_tasks > 0:
            completion_rate = (completed / total_tasks) * 100
        
        # Наиболее активный день
        tasks_by_day = defaultdict(int)
        for task in filtered_tasks:
            task_date = datetime.fromisoformat(task.get('created_at', '2000-01-01'))
            day_str = task_date.strftime('%Y-%m-%d')
            tasks_by_day[day_str] += 1
        
        most_active_day = max(tasks_by_day.items(), key=lambda x: x[1]) if tasks_by_day else ("Нет данных", 0)
        
        return {
            "period": period,
            "total_tasks": total_tasks,
            "status_distribution": dict(status_count),
            "completion_rate": round(completion_rate, 2),
            "most_active_day": {
                "date": most_active_day[0],
                "tasks_created": most_active_day[1]
            },
            "average_tasks_per_day": round(total_tasks / len(tasks_by_day), 2) if tasks_by_day else 0
        }
    
    def generate_status_report(self):
        """Генерация отчета по статусам задач"""
        if not self.tasks:
            return {"error": "Нет данных для отчета"}
        
        status_groups = defaultdict(list)
        
        for task in self.tasks:
            status = task.get('status', 'неизвестно')
            status_groups[status].append(task)
        
        report = {}
        for status, tasks in status_groups.items():
            report[status] = {
                "count": len(tasks),
                "percentage": round((len(tasks) / len(self.tasks)) * 100, 2),
                "tasks": [{"id": t.get('id'), "title": t.get('title')} for t in tasks[:5]]  # Первые 5 задач
            }
        
        return report
    
    def generate_timeline_report(self, days=30):
        """
        Генерация отчета по временной линии
        
        Args:
            days: Количество дней для анализа
        """
        if not self.tasks:
            return {"error": "Нет данных для отчета"}
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        timeline_data = []
        
        for i in range(days + 1):
            current_date = start_date + timedelta(days=i)
            date_str = current_date.strftime('%Y-%m-%d')
            
            # Подсчет задач по дням
            daily_tasks = [
                task for task in self.tasks
                if datetime.fromisoformat(task.get('created_at', '2000-01-01')).date() == current_date.date()
            ]
            
            # Статусы по дням
            status_count = defaultdict(int)
            for task in daily_tasks:
                status = task.get('status', 'неизвестно')
                status_count[status] += 1
            
            timeline_data.append({
                "date": date_str,
                "total_tasks": len(daily_tasks),
                "statuses": dict(status_count)
            })
        
        return {
            "period_days": days,
            "timeline": timeline_data
        }
    
    def generate_productivity_report(self):
        """Генерация отчета по продуктивности"""
        if not self.tasks:
            return {"error": "Нет данных для отчета"}
        
        # Группировка по дням недели
        weekday_map = {
            0: "Понедельник",
            1: "Вторник",
            2: "Среда",
            3: "Четверг",
            4: "Пятница",
            5: "Суббота",
            6: "Воскресенье"
        }
        
        weekday_stats = defaultdict(int)
        hour_stats = defaultdict(int)
        
        for task in self.tasks:
            task_date = datetime.fromisoformat(task.get('created_at', '2000-01-01'))
            
            # По дням недели
            weekday = weekday_map[task_date.weekday()]
            weekday_stats[weekday] += 1
            
            # По часам
            hour = task_date.hour
            hour_stats[hour] += 1
        
        # Наиболее продуктивные периоды
        most_productive_day = max(weekday_stats.items(), key=lambda x: x[1]) if weekday_stats else ("Нет данных", 0)
        most_productive_hour = max(hour_stats.items(), key=lambda x: x[1]) if hour_stats else (-1, 0)
        
        return {
            "by_weekday": dict(weekday_stats),
            "by_hour": dict(hour_stats),
            "most_productive": {
                "day": most_productive_day[0],
                "day_count": most_productive_day[1],
                "hour": f"{most_productive_hour[0]}:00-{most_productive_hour[0] + 1}:00",
                "hour_count": most_productive_hour[1]
            }
        }
    
    def export_to_csv(self, report_data, filename="report.csv"):
        """
        Экспорт отчета в CSV
        
        Args:
            report_data: Данные отчета
            filename: Имя файла для экспорта
        """
        try:
            # Проверяем тип отчета
            if "period" in report_data:  # Сводный отчет
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Период', 'Всего задач', 'Процент завершения', 'Самый активный день'])
                    writer.writerow([
                        report_data.get('period', 'N/A'),
                        report_data.get('total_tasks', 0),
                        f"{report_data.get('completion_rate', 0)}%",
                        f"{report_data.get('most_active_day', {}).get('date', 'N/A')} ({report_data.get('most_active_day', {}).get('tasks_created', 0)} задач)"
                    ])
                    
                    # Распределение по статусам
                    writer.writerow([])
                    writer.writerow(['Статус', 'Количество', 'Процент'])
                    for status, count in report_data.get('status_distribution', {}).items():
                        percentage = (count / report_data['total_tasks']) * 100 if report_data['total_tasks'] > 0 else 0
                        writer.writerow([status, count, f"{percentage:.2f}%"])
            
            elif "error" in report_data:
                print(f"Ошибка: {report_data['error']}")
                return False
            
            print(f"Отчет успешно экспортирован в {filename}")
            return True
            
        except Exception as e:
            print(f"Ошибка при экспорте в CSV: {e}")
            return False
    
    def export_to_json(self, report_data, filename="report.json"):
        """
        Экспорт отчета в JSON
        
        Args:
            report_data: Данные отчета
            filename: Имя файла для экспорта
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2, default=str)
            print(f"Отчет успешно экспортирован в {filename}")
            return True
        except Exception as e:
            print(f"Ошибка при экспорте в JSON: {e}")
            return False
    
    def generate_chart(self, report_type="status"):
        """
        Генерация графиков
        
        Args:
            report_type: Тип графика ("status", "timeline", "productivity")
        """
        try:
            if report_type == "status":
                report = self.generate_status_report()
                if "error" in report:
                    print(report["error"])
                    return
                
                statuses = list(report.keys())
                counts = [report[s]["count"] for s in statuses]
                
                plt.figure(figsize=(10, 6))
                plt.bar(statuses, counts, color=['green', 'blue', 'orange', 'red'])
                plt.title('Распределение задач по статусам')
                plt.xlabel('Статус')
                plt.ylabel('Количество задач')
                plt.xticks(rotation=45)
                plt.tight_layout()
                plt.savefig('status_chart.png')
                plt.show()
                
            elif report_type == "timeline":
                report = self.generate_timeline_report(days=7)
                if "error" in report:
                    print(report["error"])
                    return
                
                dates = [day["date"] for day in report["timeline"]]
                counts = [day["total_tasks"] for day in report["timeline"]]
                
                plt.figure(figsize=(12, 6))
                plt.plot(dates, counts, marker='o', linewidth=2)
                plt.title('Активность по дням (последние 7 дней)')
                plt.xlabel('Дата')
                plt.ylabel('Количество созданных задач')
                plt.xticks(rotation=45)
                plt.grid(True, alpha=0.3)
                plt.tight_layout()
                plt.savefig('timeline_chart.png')
                plt.show()
            
            print(f"График сохранен как {report_type}_chart.png")
            
        except ImportError:
            print("Для генерации графиков установите matplotlib: pip install matplotlib")
        except Exception as e:
            print(f"Ошибка при генерации графика: {e}")