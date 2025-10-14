(* Product -> Store *)
(*   |              *)
(*   v              *)
(* Order   -> User  *)

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

type user =
  { user_id  : int
  ; username : string
  ; orders   : order list
  } [@@deriving show, yojson]

let users_to_json users =
  `List (List.map user_to_yojson users)

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

let create_order (user_id: int) (product_ids: int list) : order =
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
  { order_id = Random.int 1000
  ; user_id
  ; product_ids
  ; total
  ; paid = false
  }

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

let () =
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

    ; Dream.post "/order/place" (fun req ->
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
          let order = create_order user_id product_ids in
          order_to_yojson order |> ok_json)
    ]