import React, { useState } from "react";
import FormInput from "./FormInput";
import axios from "axios";
import CustomerTable from "./CustomerTable";
import WarningTable from "./WarningTable";

export default function AdminPanel() {
  const [isValid, setIsValid] = useState(false);
  const [creditInput, setCreditInput] = useState({
    Admin_Name: "",
    Password: "",
  });
  const [resultData, setResultData] = useState();

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await axios.post(
        "http://localhost:9000/admin",
        creditInput
      );
      // Flatten the customerDetails array
      const flattenedCustomerDetails = response.data.Customer_Info.customerDetails.flat();
      setResultData({ ...response.data.Customer_Info, customerDetails: flattenedCustomerDetails });
      setIsValid(response.data.Customer_Info.isValid === "true");
    } catch (error) {
      console.error("Error", error);
    }
  };

  function handleChange(event) {
    const { name, value } = event.target;

    setCreditInput((prevVal) => {
      return {
        ...prevVal,
        [name]: value,
      };
    });
  }

  const filteredAlerts =
    resultData?.alerts?.filter((alert) =>
      ["Initial", "Critical", "NPA"].includes(alert.alert)
    ) || [];

  const bgStyle = null;

  return (
    <>
      <div className="d-flex justify-content-center">
        <div className="col-md-11 border p-2 bg-body-secondary rounded-4">
          <form
            action=""
            method=""
            className="need-validation mt-5"
            noValidate
            encType="multipart/form-data"
            onSubmit={handleSubmit}
          >
            <div className="d-flex justify-content-center">
              <div className="col-md-11 p-3 d-flex justify-content-evenly">
                <div className="col-md-5 border p-3">
                  <FormInput
                    label="Admin :"
                    type="text"
                    name="Admin_Name"
                    placeholder=""
                    onChange={handleChange}
                  />
                </div>
                <div className="col-md-5 border p-3">
                  <FormInput
                    label="Password :"
                    type="password"
                    name="Password"
                    onChange={handleChange}
                  />
                </div>
              </div>
            </div>
            <div className="p-3 mt-3 d-flex justify-content-center">
              <button type="submit" className="btn btn-success rounded-5">
                <span className="">Find User Info</span>
              </button>
            </div>
          </form>
        </div>
      </div>
      {isValid && resultData && (
        <div className="mt-5 d-flex justify-content-center">
          <div className="col-md-11 border p-3 bg-body-secondary rounded-4">
            <div className="col-md-12 d-flex justify-content-between">
              <div className="col-md-5 p-3">
                <h1 className="fw-bolder text-center">Admin Panel</h1>
              </div>
              <div className="col-md-5 p-3">
                <h3 className="fw-bolder text-end">Notify</h3>
              </div>
            </div>
            <hr />
            <WarningTable
              filterLength={filteredAlerts.length}
              filteredAlerts={filteredAlerts}
              resultData={resultData}
            />
            <hr />
            {/* Customer Table */}
            <CustomerTable
              resultData={resultData}
              resultLength={resultData.customerDetails.length}
            />
            <br />
            <hr />
          </div>
        </div>
      )}
    </>
  );
}
