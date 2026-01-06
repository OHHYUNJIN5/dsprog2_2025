import flet as ft
import requests

AREA_URL = "https://www.jma.go.jp/bosai/common/const/area.json"
FORECAST_URL = "https://www.jma.go.jp/bosai/forecast/data/forecast/{code}.json"


def fetch_area_data() -> dict:
    
    resp = requests.get(AREA_URL, timeout=10)
    resp.raise_for_status()
    return resp.json()


def build_office_list(area_json: dict) -> list[tuple[str, str]]:
   
    offices = area_json.get("offices", {})
    items = []
    for code, info in offices.items():
        name = info.get("name", code)
        items.append((name, code))

    
    items.sort(key=lambda x: x[0])
    return items


def fetch_forecast(code: str) -> list:
    url = FORECAST_URL.format(code=code)
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()


def extract_daily_cards(forecast_json: list) -> list[ft.Control]:
    
    
    if not forecast_json:
        return [ft.Text("예보 데이터가 비어있음")]

    try:
        ts0 = forecast_json[0]["timeSeries"][0]
        times = ts0.get("timeDefines", [])
        areas = ts0.get("areas", [])

        if not areas:
            return [ft.Text("예보 areas가 없음")]

        area0 = areas[0]
        weathers = area0.get("weathers", [])

        cards: list[ft.Control] = []
        for i, t in enumerate(times):
            date_str = t.split("T")[0] if isinstance(t, str) else str(t)
            weather_text = weathers[i] if i < len(weathers) else "(날씨 정보 없음)"

            cards.append(
                ft.Card(
                    content=ft.Container(
                        padding=12,
                        width=280,
                        content=ft.Column(
                            tight=True,
                            spacing=6,
                            controls=[
                                ft.Text(date_str, size=14, weight=ft.FontWeight.BOLD),
                                ft.Text(weather_text, size=12),
                            ],
                        ),
                    )
                )
            )
        return cards if cards else [ft.Text("표시할 예보가 없음")]

    except Exception as e:
        return [ft.Text(f"예보 파싱 중 오류: {e}")]


def main(page: ft.Page):
    page.title = "天気予報アプリ (JMA API)"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 12

   
    title = ft.Text("地域を選択してください", size=18, weight=ft.FontWeight.BOLD)
    content_area = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, controls=[title])

   
    try:
        area_json = fetch_area_data()
        office_items = build_office_list(area_json)  # (name, code)
    except Exception as e:
        page.add(ft.Text(f"地域リスト取得に失敗: {e}"))
        return

    
    left_list = ft.ListView(expand=True, spacing=2, padding=8)
    count_text = ft.Text(f"地域数: {len(office_items)}", size=12, color=ft.Colors.WHITE70)

    def select_area(name: str, code: str):
        title.value = f"{name}（{code}）の天気予報"
        content_area.controls = [title, ft.ProgressRing()]
        page.update()

        try:
            forecast_json = fetch_forecast(code)
            cards = extract_daily_cards(forecast_json)
            content_area.controls = [
                title,
                ft.Row(
                wrap=True,              
                spacing=10,
                run_spacing=10,
                controls=cards,)
,
            ]
        except Exception as ex:
            content_area.controls = [title, ft.Text(f"予報取得に失敗: {ex}")]
        page.update()

 
    for (name, code) in office_items:
        left_list.controls.append(
            ft.ListTile(
                title=ft.Text(name),
                subtitle=ft.Text(code),
                on_click=lambda e, n=name, c=code: select_area(n, c),
            )
        )

    left_panel = ft.Container(
        width=340,
        bgcolor=ft.Colors.BLUE_GREY_900,
        border_radius=12,
        padding=10,
        content=ft.Column(
            expand=True,
            controls=[
                ft.Text("地域を選択", size=16, weight=ft.FontWeight.BOLD),
                count_text,
                ft.Divider(),
                left_list,
            ],
        ),
    )

    right_panel = ft.Container(
        expand=True,
        padding=10,
        content=content_area,
        bgcolor=ft.Colors.BLUE_GREY_800,
        border_radius=12,
    )

    page.add(
        ft.Row(
            expand=True,
            controls=[
                left_panel,
                ft.VerticalDivider(width=12, thickness=0),
                right_panel,
            ],
        )
    )


if __name__ == "__main__":
    ft.app(target=main)
