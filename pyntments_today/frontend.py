import json
import time

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from nicegui import events, ui

from pyntments_today.constants import WORKING_DIR


def save_appointments(appointments: list[dict]):
    print("save...")
    appointments_json_file_path = WORKING_DIR / "appointments.json"
    appointments_json_file_path.write_text(json.dumps(appointments, indent=4))


def load_appointments() -> list[dict]:
    print("load...")
    appointments_json_file_path = WORKING_DIR / "appointments.json"
    return json.loads(appointments_json_file_path.read_text())


def init(fastapi_app: FastAPI) -> None:
    columns = [
        {"name": "time", "label": "Zeit", "field": "time", "align": "left"},
        {
            "name": "appointment",
            "label": "Aufgabe / Termin",
            "field": "appointment",
            "align": "left",
        },
    ]
    rows = load_appointments()

    @ui.page("/appointments")
    async def show_appointments():
        table = ui.table(columns=columns, rows=rows, row_key="time").classes("w-full")
        table.add_slot(
            "header",
            r"""
            <q-tr :props="props" class="bg-blue-800">
                <q-th v-for="col in props.cols" :key="col.name" :props="props">
                    <span class="text-base font-bold text-white">{{ col.label }}</span>
                </q-th>
            </q-tr>
        """,
        )
        table.add_slot(
            "body",
            r"""
                 <q-tr :props="props">
                     <q-td key="time" :props="props" class="font-bold w-[100px] text-blue-800">
                         <span style="white-space: pre;" class="text-base">{{ props.row.time }}<span>
                     </q-td>
                     <q-td key="appointment" :props="props" class="font-bold flex-1">
                         <span style="white-space: pre;" class="text-base">{{ props.row.appointment }}</span>
                     </q-td>
                 </q-tr>
             """,
        )

    @ui.page("/appointments/edit")
    async def edit_appointments():
        def add_row() -> None:
            new_id = max((dx["id"] for dx in rows), default=-1) + 1
            rows.append({"id": new_id, "time": "... - ...", "appointment": "..."})
            ui.notify(f"Added new row with ID {new_id}")
            table.update()
            save_appointments(rows)

        def rename(e: events.GenericEventArguments) -> None:
            for row in rows:
                if row["id"] == e.args["id"]:
                    row.update(e.args)
            ui.notify(f"Updated rows to: {table.rows}")
            table.update()
            save_appointments(rows)

        def delete(e: events.GenericEventArguments) -> None:
            rows[:] = [row for row in rows if row["id"] != e.args["id"]]
            ui.notify(f'Deleted row with ID {e.args["id"]}')
            table.update()
            save_appointments(rows)

        table = ui.table(columns=columns, rows=rows, row_key="time").classes("w-full")
        table.add_slot(
            "header",
            r"""
            <q-tr :props="props">
                <q-th/>
                <q-th v-for="col in props.cols" :key="col.name" :props="props">
                    {{ col.label }}
                </q-th>
            </q-tr>
        """,
        )
        table.add_slot(
            "body",
            r"""
            <q-tr :props="props">
                <q-td class="w-[40px]">
                    <q-btn size="sm" color="warning" round dense icon="delete"
                        @click="() => $parent.$emit('delete', props.row)"
                    />
                </q-td>
                <q-td key="time" :props="props" class="w-[120px]">
                    <span style="white-space: pre;">{{ props.row.time }}</span>
                    <q-popup-edit v-model="props.row.time" v-slot="scope" buttons
                        @update:model-value="() => $parent.$emit('rename', props.row)"
                    >
                        <q-input type="textarea" v-model="scope.value" autofocus counter  @keyup.enter.stop />
                    </q-popup-edit>
                </q-td>
                <q-td key="appointment" :props="props" class="flex-1">
                    <span style="white-space: pre;">{{ props.row.appointment }}</span>
                    <q-popup-edit v-model="props.row.appointment" v-slot="scope" buttons
                        @update:model-value="() => $parent.$emit('rename', props.row)"
                    >
                        <q-input type="textarea" v-model="scope.value" autofocus counter  @keyup.enter.stop />
                    </q-popup-edit>
                </q-td>
            </q-tr>
        """,
        )
        with table.add_slot("bottom-row"):
            with table.cell().props("colspan=3"):
                ui.button(
                    "Add row", icon="add", color="accent", on_click=add_row
                ).classes("w-full")
        table.on("rename", rename)
        table.on("delete", delete)

    ui.run_with(
        fastapi_app,
        mount_path="",  # NOTE this can be omitted if you want the paths passed to @ui.page to be at the root
    )
