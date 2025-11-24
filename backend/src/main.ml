(* ============================== *)
(* Types                          *)
(* ============================== *)

type product =
  { product_id : int
  ; name       : string
  ; price      : float
  } [@@deriving show, yojson]

let products_to_json products =
  `List (List.map product_to_yojson products)

type store =
  { store_id : int
  ; name     : string
  ; products : product list
  } [@@deriving show, yojson]

let stores_to_json stores =
  `List (List.map store_to_yojson stores)

type order =
  { order_id    : int
  ; user_id     : int (* Reference to user ID *)
  ; product_ids : int list
  ; total       : float
  ; paid        : bool
  } [@@deriving show, yojson]

let orders_to_json orders =
  `List (List.map order_to_yojson orders)

let order_t : order Caqti_type.t =
  let encode { order_id; user_id; product_ids; total; paid } =
    Ok ( order_id
       , user_id
       , Yojson.Safe.to_string
          (`List (List.map (fun i -> `Int i) product_ids))
       , total
       , paid)
  in
  let decode (order_id, user_id, product_ids_json, total, paid) =
    match Yojson.Safe.from_string product_ids_json with
    | `List lst ->
      let product_ids =
        List.filter_map (function `Int i -> Some i | _ -> None) lst
      in
      Ok { order_id; user_id; product_ids; total; paid }
    | _ -> Error "Expected JSON list for product_ids"
  in
  Caqti_type.custom
    ~encode
    ~decode
    Caqti_type.(t5 int int string float bool)

type user =
  { user_id   : int
  ; username  : string
  ; password  : string (* hashed password *)
  ; user_type : string (* "USER" | "STORE" | "ADMIN" *)
  } [@@deriving show, yojson]

let example_stores: store list =
  [ { store_id = 1
    ; name = "Foo Store"
    ; products =
      [ { product_id = 1; name = "Apple"; price = 1.00 }
      ; { product_id = 2; name = "Banana"; price = 1.50 }
      ]
    }
  ; { store_id = 2
    ; name = "Bar Store"
    ; products =
      [ { product_id = 3; name = "Orange"; price = 1.50 }
      ; { product_id = 4; name = "Grapes"; price = 2.00 }
      ]
    }
  ]

let create_order (order_id: int) (user_id: int) (product_ids: int list) : order =
  let total = List.fold_left (fun acc pid ->
      (* Try to find a product with the given product_id (pid) in all example
        stores *)
      match List.find_opt
        (* Predicate: checks if a product's id matches the target *)
        (fun p -> p.product_id = pid)
        (* Flatten all products from all stores into a single list *)
        (List.flatten (List.map (fun s -> s.products) example_stores)) with
      (* If a matching product is found, add its price to the accumulator *)
      | Some product -> acc +. product.price
      (* If not found, just return the accumulator unchanged *)
      | None -> acc
    ) 0.0 product_ids in
  { order_id
  ; user_id
  ; product_ids
  ; total
  ; paid = false
  }

(* ============================== *)
(* Utility                        *)
(* ============================== *)

let ok_json obj =
  Dream.response
    ~status:`OK
    ~headers:[("Content-Type", "application/json")]
    (Yojson.Safe.pretty_to_string obj)
  |> Lwt.return

let not_found msg =
  Dream.response
    ~status:`Not_Found
    ~headers:[("Content-Type", "application/json")]
    (Yojson.Safe.pretty_to_string (`Assoc [("error", `String msg)]))
  |> Lwt.return

let bad_request msg =
  Dream.response
    ~status:`Bad_Request
    ~headers:[("Content-Type", "application/json")]
    (Yojson.Safe.pretty_to_string (`Assoc [("error", `String msg)]))
  |> Lwt.return

let to_list_option = function
  | `List lst -> Some lst
  | _ -> None

(* ============================== *)
(* State                          *)
(* ============================== *)

type state =
  { mutable stores: store list
  ; mutable orders: order list
  ; mutable users:  user  list
  ; mutable until_replicate: int
  }

let state_new () =
  { stores = example_stores
  ; orders = []
  ; users  = []
  ; until_replicate = 0
  }

let state_save state =
  let query1 =
    let open Caqti_request.Infix in
    (* Insert orders by clearing the table first *)
    (Caqti_type.unit ->. Caqti_type.unit) "DELETE FROM orders"
  in

  let query2 =
    let open Caqti_request.Infix in
    (Caqti_type.(t5 int int string float bool) ->. Caqti_type.unit)
    "INSERT INTO orders (order_id, user_id, product_ids, total, paid)
     VALUES (?, ?, ?, ?, ?)"
  in

  (fun (module Db: Caqti_lwt.CONNECTION) ->
    let%lwt res = Db.exec query1 () in
    match res with
    | Error _ as e -> Lwt.return e
    | Ok () ->
      let rec insert_orders = function
        | [] -> Lwt.return (Ok ())
        | o :: os ->
          let%lwt res = Db.exec query2 (o.order_id, o.user_id,
            Yojson.Safe.to_string
              (`List (List.map (fun i -> `Int i) o.product_ids)),
            o.total, o.paid) in
          match res with
          | Ok () -> insert_orders os
          | Error _ as e -> Lwt.return e
      in
      insert_orders state.orders)

let state_replicate_if_could state (r: Dream.request) =
  if state.until_replicate <= 0 then begin
    state.until_replicate <- 5;
    Dream.log "Replicating to database";
    let%lwt res = Dream.sql r (state_save state) in
    match res with
    | Ok () ->
      Dream.log "Replication successful";
      Lwt.return ()
    | Error err -> Dream.log "Replication error: %s"
        (Caqti_error.show err);
    Lwt.return ()
  end else begin
    state.until_replicate <- state.until_replicate - 1;
    Lwt.return ()
  end

let state_get_order state order_id =
  List.find_opt (fun o -> o.order_id = order_id) state.orders

let state_filter_orders state f =
  List.filter f state.orders

let state_add_order state order =
  state.orders <- order :: state.orders

let state_create_user state username password user_type =
  let id = List.length state.users in
  state.users <- { user_id = id; username; password; user_type } :: state.users;
  id

(* ============================== *)
(* Auth                           *)
(* ============================== *)

let user_sign_up (username: string) (password: string) =
  let payload =
    [ ("username", username)
    ; ("password", password)
    ] in
  let hash = Jwto.encode Jwto.HS256 "secret" payload in
  match hash with
  | Ok token ->
    let query =
      let open Caqti_request.Infix in
      (Caqti_type.(t3 string string string) ->. Caqti_type.unit)
      "INSERT INTO users (username, password, user_type)
       VALUES (?, ?, ?)" in
    Ok (token,
      { user_id = 0 (* Placeholder, should be from DB *)
      ; username
      ; password
      ; user_type = "USER"
      })
  | Error _ -> Error "Failed to generate JWT token"

(* ============================== *)
(* Entry                          *)
(* ============================== *)

let () =
  let s = ref (state_new ()) in

  Dream.run
  @@ Dream.logger
  @@ Dream.sql_pool "sqlite3:data.sqlite"
  @@ Dream.sql_sessions
  @@ Dream.router
    [ Dream.get "/" (fun _ -> Dream.json {| { "message": "Hello, World!" } |})

    ; Dream.get "/stores" (fun _ -> stores_to_json example_stores |> ok_json)

    ; Dream.get "/stores/:id" (fun req ->
      let id = Dream.param req "id" |> int_of_string in

      match List.find_opt (fun s -> s.store_id = id) example_stores with
      | Some store -> store_to_yojson store |> ok_json
      | None -> not_found "Store not found")

    ; Dream.get "/order" (fun _ ->
      orders_to_json !s.orders |> ok_json)

    ; Dream.get "/order/:id" (fun req ->
      let id = Dream.param req "id" |> int_of_string in
      let orders = state_filter_orders !s (fun o ->
        (* Check what stores the product_ids is from and filter it to the id *)
        List.exists (fun pid ->
          List.exists (fun store ->
            store.store_id = id &&
            List.exists (fun p -> p.product_id = pid) store.products
          ) example_stores
        ) o.product_ids
      ) in
      ok_json (orders_to_json orders))

    ; Dream.post "/order/place" (fun req ->
      (* curl -X POST http://localhost:8080/order/place \
         -H "Content-Type: application/json" \
         -d '{ "user_id": 1, "product_ids": [1, 2] }' *)
      let%lwt body = Dream.body req in

      let json = try Yojson.Safe.from_string body with
        | Yojson.Json_error err ->
          Dream.log "JSON Parse Error: %s" err;
          `Null
      in

      match json with
      | `Null -> bad_request "Invalid JSON"
      | json ->
        (* Get user_id and product_ids from JSON *)
        let user_id = match Yojson.Safe.Util.(json
            |> member "user_id"
            |> to_int_option) with
          | Some id -> id
          | None ->
            Dream.log "Missing or invalid user_id";
            -1
        in
        let product_ids = match Yojson.Safe.Util.(json
            |> member "product_ids"
            |> to_list_option) with
          | Some lst ->
            List.filter_map Yojson.Safe.Util.to_int_option lst
          | None ->
            Dream.log "Missing or invalid product_ids";
            []
        in

        if user_id = -1 || product_ids = [] then
          bad_request "Invalid user_id or product_ids"
        else
          let id = List.length !s.orders in
          let order = create_order id user_id product_ids in
          let%lwt _ = state_add_order !s order req in
          order_to_yojson order |> ok_json)
          ]